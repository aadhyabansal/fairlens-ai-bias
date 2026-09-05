import pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from fairlearn.reductions import ExponentiatedGradient, DemographicParity, EqualizedOdds
from sklearn.metrics import accuracy_score

from app.schemas.audit import MitigationRequest, MitigationResult
from app.engine.validation import load_and_validate
from app.engine.metrics import train_baseline, compute_fairness_metrics


def _get_constraint_object(constraint: str):
    if constraint == "demographic_parity":
        return DemographicParity()
    elif constraint == "equalized_odds":
        return EqualizedOdds()
    else:
        raise ValueError(f"Unknown constraint: {constraint}")


def run_mitigation(request: MitigationRequest) -> MitigationResult:
    from app.schemas.audit import AuditRequest

    audit_request = AuditRequest(
        dataset_path=request.dataset_path,
        target_column=request.target_column,
        sensitive_attributes=[request.sensitive_attribute],
    )
    df, dataset_warnings = load_and_validate(audit_request)

    baseline = train_baseline(df, request.target_column, [request.sensitive_attribute])
    model = baseline["model"]
    X_train, X_test = baseline["X_train"], baseline["X_test"]
    y_train, y_test = baseline["y_train"], baseline["y_test"]
    df_test = baseline["df_test"]

    # sensitive_train = df_test.loc[X_train.index, request.sensitive_attribute] \
    #     if False else None  # placeholder, corrected below


    # Original (unmitigated) predictions and metrics
    original_pred = model.predict(X_test)
    original_accuracy = accuracy_score(y_test, original_pred)
    original_metrics = compute_fairness_metrics(
        request.sensitive_attribute, y_test, original_pred, df_test, dataset_warnings
    )

    # We need the sensitive attribute aligned to X_train for fitting mitigators
    sensitive_train_series = df.loc[X_train.index, request.sensitive_attribute]
    sensitive_test_series = df_test[request.sensitive_attribute]

    if request.technique == "threshold_optimizer":
        mitigator = ThresholdOptimizer(
            estimator=model,
            constraints="demographic_parity" if request.constraint == "demographic_parity" else "equalized_odds",
            predict_method="predict",
            prefit=True,
        )
        mitigator.fit(X_train, y_train, sensitive_features=sensitive_train_series)
        mitigated_pred = mitigator.predict(X_test, sensitive_features=sensitive_test_series)

    elif request.technique == "exponentiated_gradient":
        constraint_obj = _get_constraint_object(request.constraint)
        mitigator = ExponentiatedGradient(estimator=model, constraints=constraint_obj)
        mitigator.fit(X_train, y_train, sensitive_features=sensitive_train_series)
        mitigated_pred = mitigator.predict(X_test)

    else:
        raise ValueError(f"Unknown technique: {request.technique}")

    mitigated_accuracy = accuracy_score(y_test, mitigated_pred)
    mitigated_metrics = compute_fairness_metrics(
        request.sensitive_attribute, y_test, mitigated_pred, df_test, dataset_warnings
    )

    return MitigationResult(
        technique=request.technique,
        constraint=request.constraint,
        original_metrics=original_metrics,
        mitigated_metrics=mitigated_metrics,
        original_accuracy=float(original_accuracy),
        mitigated_accuracy=float(mitigated_accuracy),
        accuracy_cost=float(original_accuracy - mitigated_accuracy),
    )