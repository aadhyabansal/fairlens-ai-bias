import pytest
from app.engine.validation import load_and_validate, ValidationError
from app.schemas.audit import AuditRequest


def test_valid_adult_dataset():
    request = AuditRequest(
        dataset_path="data/samples/adult_income.csv",
        target_column="income",
        sensitive_attributes=["sex", "race"],
    )
    df, warnings = load_and_validate(request)
    assert len(df) > 0

    print(f"Warnings: {warnings}")


def test_missing_target_column():
    request = AuditRequest(
        dataset_path="data/samples/adult_income.csv",
        target_column="not_a_real_column",
        sensitive_attributes=["sex"],
    )
    with pytest.raises(ValidationError):
        load_and_validate(request)