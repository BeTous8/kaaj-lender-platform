from pydantic import BaseModel
from app.models.policy_rule import RuleOperator


class PolicyRuleCreate(BaseModel):
    field_name: str
    operator: RuleOperator
    value: str
    is_hard_stop: bool = False
    description: str | None = None


class PolicyRuleUpdate(BaseModel):
    field_name: str | None = None
    operator: RuleOperator | None = None
    value: str | None = None
    is_hard_stop: bool | None = None
    description: str | None = None


class PolicyRuleOut(BaseModel):
    id: int
    program_id: int
    field_name: str
    operator: RuleOperator
    value: str
    is_hard_stop: bool
    description: str | None

    model_config = {"from_attributes": True}