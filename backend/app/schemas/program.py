from pydantic import BaseModel
from .policy_rule import PolicyRuleOut


class ProgramCreate(BaseModel):
    lender_id: int
    name: str
    priority: int = 0
    is_active: bool = True


class ProgramOut(BaseModel):
    id: int
    lender_id: int
    name: str
    priority: int
    is_active: bool
    policy_rules: list[PolicyRuleOut] = []

    model_config = {"from_attributes": True}