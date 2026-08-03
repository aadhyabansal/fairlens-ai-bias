import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from fairlearn.metrics import MetricFrame, selection_rate
from sklearn.metrics import accuracy_score

from app.schemas.audit import AuditRequest, AuditResult, FairnessMetrics, SubgroupMetrics
from app.engine.validation import load_and_validate 


def false_positive_rate(y_true, y_pred):
    fp = ((y_pred == 1) & (y_true == 0)).sum()
    negatives = (y_true == 0).sum()
    return fp / negatives if negatives > 0 else 0.0


def false_negative_rate(y_true, y_pred):
    fn = ((y_pred == 0) & (y_true == 1)).sum()
    positives = (y_true == 1).sum()
    return fn / positives if positives > 0 else 0.0


def _prepare_features(df: pd.DataFrame, target_column: str, sensitive_attributes: list[str]):
    """
    Encodes categorical features numerically so a baseline model can train.
    Sensitive attributes are EXCLUDED from training features deliberately.
    """
    feature_df = df.drop(columns=[target_column] + sensitive_attributes)

    # Simple label encoding for any categorical columns
    for col in feature_df.select_dtypes(include=["object", "category"]).columns:
        feature_df[col] = LabelEncoder().fit_transform(feature_df[col].astype(str))

    return feature_df


def run_audit(request: AuditRequest) -> AuditResult:
    df, dataset_warnings = load_and_validate(request)

    y = df[request.target_column].astype(int)
    X = _prepare_features(df, request.target_column, request.sensitive_attributes)

    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X, y, df, test_size=0.3, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    overall_accuracy = accuracy_score(y_test, y_pred)

    metrics_by_attribute = []

    for attr in request.sensitive_attributes:
        sensitive_test = df_test[attr]

        mf = MetricFrame(
            metrics={
                "selection_rate": selection_rate,
                "false_positive_rate": false_positive_rate,
                "false_negative_rate": false_negative_rate,
                "accuracy": accuracy_score,
            },
            y_true=y_test,
            y_pred=y_pred,
            sensitive_features=sensitive_test,
        )

        subgroups = []
        for group_name in mf.by_group.index:
            row = mf.by_group.loc[group_name]
            subgroups.append(SubgroupMetrics(
                group_name=str(group_name),
                sample_size=int((sensitive_test == group_name).sum()),
                selection_rate=float(row["selection_rate"]),
                false_positive_rate=float(row["false_positive_rate"]),
                false_negative_rate=float(row["false_negative_rate"]),
                accuracy=float(row["accuracy"]),
            ))

        selection_rates = mf.by_group["selection_rate"]
        dpd = float(selection_rates.max() - selection_rates.min())

        fpr_diff = float(mf.by_group["false_positive_rate"].max() - mf.by_group["false_positive_rate"].min())
        fnr_diff = float(mf.by_group["false_positive_rate"].max() - mf.by_group["false_negative_rate"].min())
        eod = max(fpr_diff, fnr_diff)

        min_rate = selection_rates.min()
        max_rate = selection_rates.max()
        dir_ratio = float(min_rate / max_rate) if max_rate > 0 else 0.0

        attr_warnings = [w for w in dataset_warnings if attr in w]

        metrics_by_attribute.append(FairnessMetrics(
            sensitive_attribute=attr,
            demographic_parity_difference=dpd,
            equalized_odds_difference=eod,
            disparate_impact_ratio=dir_ratio,
            subgroups=subgroups,
            warnings=attr_warnings,
        ))

    return AuditResult(
        dataset_path=request.dataset_path,
        target_column=request.target_column,
        overall_accuracy=float(overall_accuracy),
        metrics_by_attribute=metrics_by_attribute,
    )