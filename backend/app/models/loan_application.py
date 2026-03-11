import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
from app.db import Base


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    years_in_business: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    fico_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    paynet_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transunion_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    loan_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    equipment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    equipment_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    equipment_mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_startup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_bankruptcy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bankruptcy_years_ago: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_judgments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_repossessions: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_tax_liens: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_us_citizen: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    match_results: Mapped[list["MatchResult"]] = relationship(
        "MatchResult", back_populates="application", cascade="all, delete-orphan"
    )