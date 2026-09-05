from pydantic import BaseModel, Field
from typing import Optional


class SubgroupMetrics(BaseModel):
    group_name: str
    sample_size: int
    selection_rate: float          # P(prediction = positive) for this group
    false_positive_rate: float
    false_negative_rate: float
    accuracy: float


class FairnessMetrics(BaseModel):
    sensitive_attribute: str
    demographic_parity_difference: float
    equalized_odds_difference: float
    disparate_impact_ratio: float
    subgroups: list[SubgroupMetrics]
    warnings: list[str] = Field(default_factory=list)  # e.g. small-subgroup flags


class AuditRequest(BaseModel):
    dataset_path: str
    target_column: str
    sensitive_attributes: list[str]


class AuditResult(BaseModel):
    dataset_path: str
    target_column: str
    overall_accuracy: float
    metrics_by_attribute: list[FairnessMetrics]

class MitigationResult(BaseModel):
    technique: str  # "threshold_optimizer" or "exponentiated_gradient"
    constraint: str  # "demographic_parity" or "equalized_odds"
    original_metrics: FairnessMetrics
    mitigated_metrics: FairnessMetrics
    original_accuracy: float
    mitigated_accuracy: float
    accuracy_cost: float  # original_accuracy - mitigated_accuracy


class MitigationRequest(BaseModel):
    dataset_path: str
    target_column: str
    sensitive_attribute: str  # single attribute — mitigation techniques constrain on ONE at a time
    technique: str  # "threshold_optimizer" or "exponentiated_gradient"
    constraint: str = "demographic_parity"  # or "equalized_odds"