from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lender_id: Mapped[int] = mapped_column(ForeignKey("lenders.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    lender: Mapped["Lender"] = relationship("Lender", back_populates="programs")
    policy_rules: Mapped[list["PolicyRule"]] = relationship(
        "PolicyRule", back_populates="program", cascade="all, delete-orphan"
    )
    match_results: Mapped[list["MatchResult"]] = relationship(
        "MatchResult", back_populates="program"
    )
