from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class RuleEvaluation(Base):
    __tablename__ = "rule_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_result_id: Mapped[int] = mapped_column(ForeignKey("match_results.id"), nullable=False, index=True)
    policy_rule_id: Mapped[int] = mapped_column(ForeignKey("policy_rules.id"), nullable=False, index=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    actual_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    match_result: Mapped["MatchResult"] = relationship("MatchResult", back_populates="rule_evaluations")
    policy_rule: Mapped["PolicyRule"] = relationship("PolicyRule", back_populates="rule_evaluations")