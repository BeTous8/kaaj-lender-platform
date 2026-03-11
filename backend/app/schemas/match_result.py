from datetime import datetime
from pydantic import BaseModel
from .rule_evaluation import RuleEvaluationOut


class MatchResultOut(BaseModel):
    id: int
    application_id: int
    lender_id: int
    program_id: int
    is_eligible: bool
    fit_score: float | None
    created_at: datetime
    rule_evaluations: list[RuleEvaluationOut] = []

    model_config = {"from_attributes": True}