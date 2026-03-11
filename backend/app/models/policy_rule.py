import enum
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
from app.db import Base


class RuleOperator(str, enum.Enum):
    gte = "gte"
    lte = "lte"
    gt = "gt"
    lt = "lt"
    equals = "equals"
    not_in = "not_in"
    in_ = "in"


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[RuleOperator] = mapped_column(SAEnum(RuleOperator, name="rule_operator"), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    is_hard_stop: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    program: Mapped["Program"] = relationship("Program", back_populates="policy_rules")
    rule_evaluations: Mapped[list["RuleEvaluation"]] = relationship(
        "RuleEvaluation", back_populates="policy_rule"
    )