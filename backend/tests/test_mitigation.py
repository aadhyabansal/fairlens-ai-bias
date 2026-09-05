from app.engine.mitigation import run_mitigation
from app.schemas.audit import MitigationRequest


def test_threshold_optimizer_demographic_parity():
    request = MitigationRequest(
        dataset_path="data/samples/adult_income.csv",
        target_column="income",
        sensitive_attribute="sex",
        technique="threshold_optimizer",
        constraint="demographic_parity",
    )
    result = run_mitigation(request)

    print(f"\nOriginal accuracy: {result.original_accuracy:.3f}")
    print(f"Mitigated accuracy: {result.mitigated_accuracy:.3f}")
    print(f"Accuracy cost: {result.accuracy_cost:.3f}")
    print(f"Original DPD: {result.original_metrics.demographic_parity_difference:.3f}")
    print(f"Mitigated DPD: {result.mitigated_metrics.demographic_parity_difference:.3f}")

    # Mitigation should reduce the demographic parity gap
    assert result.mitigated_metrics.demographic_parity_difference < result.original_metrics.demographic_parity_difference


def test_exponentiated_gradient_demographic_parity():
    request = MitigationRequest(
        dataset_path="data/samples/adult_income.csv",
        target_column="income",
        sensitive_attribute="sex",
        technique="exponentiated_gradient",
        constraint="demographic_parity",
    )
    result = run_mitigation(request)

    print(f"\nOriginal accuracy: {result.original_accuracy:.3f}")
    print(f"Mitigated accuracy: {result.mitigated_accuracy:.3f}")
    print(f"Accuracy cost: {result.accuracy_cost:.3f}")
    print(f"Original DPD: {result.original_metrics.demographic_parity_difference:.3f}")
    print(f"Mitigated DPD: {result.mitigated_metrics.demographic_parity_difference:.3f}")

    assert result.mitigated_metrics.demographic_parity_difference < result.original_metrics.demographic_parity_difference