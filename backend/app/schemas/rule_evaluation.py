from pydantic import BaseModel


class RuleEvaluationOut(BaseModel):
    id: int
    match_result_id: int
    policy_rule_id: int
    passed: bool
    actual_value: str | None
    required_value: str | None
    explanation: str | None

    model_config = {"from_attributes": True}