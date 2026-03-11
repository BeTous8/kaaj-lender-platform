from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("loan_applications.id"), nullable=False, index=True)
    lender_id: Mapped[int] = mapped_column(ForeignKey("lenders.id"), nullable=False, index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False, index=True)
    is_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    application: Mapped["LoanApplication"] = relationship("LoanApplication", back_populates="match_results")
    lender: Mapped["Lender"] = relationship("Lender", back_populates="match_results")
    program: Mapped["Program"] = relationship("Program", back_populates="match_results")
    rule_evaluations: Mapped[list["RuleEvaluation"]] = relationship(
        "RuleEvaluation", back_populates="match_result", cascade="all, delete-orphan"
    )
