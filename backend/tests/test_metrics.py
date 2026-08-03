from app.engine.metrics import run_audit
from app.schemas.audit import AuditRequest


def test_adult_income_audit():
    request = AuditRequest(
        dataset_path="data/samples/adult_income.csv",
        target_column="income",
        sensitive_attributes=["sex", "race"],
    )
    result = run_audit(request)

    print(f"\nOverall accuracy: {result.overall_accuracy:.3f}")
    for m in result.metrics_by_attribute:
        print(f"\n--- {m.sensitive_attribute} ---")
        print(f"Demographic parity diff: {m.demographic_parity_difference:.3f}")
        print(f"Equalized odds diff: {m.equalized_odds_difference:.3f}")
        print(f"Disparate impact ratio: {m.disparate_impact_ratio:.3f}")
        for sg in m.subgroups:
            print(f"  {sg.group_name}: n={sg.sample_size}, selection_rate={sg.selection_rate:.3f}")

    # Adult Income is known to show a meaningful gender gap
    sex_metrics = next(m for m in result.metrics_by_attribute if m.sensitive_attribute == "sex")
    assert sex_metrics.demographic_parity_difference > 0.1