from datetime import datetime
from pydantic import BaseModel
from app.models.loan_application import ApplicationStatus


class LoanApplicationCreate(BaseModel):
    business_name: str
    industry: str | None = None
    state: str | None = None
    years_in_business: float | None = None
    annual_revenue: float | None = None
    fico_score: int | None = None
    paynet_score: int | None = None
    transunion_score: int | None = None
    loan_amount: float | None = None
    equipment_type: str | None = None
    equipment_year: int | None = None
    equipment_mileage: int | None = None
    is_startup: bool = False
    has_bankruptcy: bool = False
    bankruptcy_years_ago: float | None = None
    has_judgments: bool = False
    has_repossessions: bool = False
    has_tax_liens: bool = False
    is_us_citizen: bool = True


class LoanApplicationOut(BaseModel):
    id: int
    business_name: str
    industry: str | None
    state: str | None
    years_in_business: float | None
    annual_revenue: float | None
    fico_score: int | None
    paynet_score: int | None
    transunion_score: int | None
    loan_amount: float | None
    equipment_type: str | None
    equipment_year: int | None
    equipment_mileage: int | None
    is_startup: bool
    has_bankruptcy: bool
    bankruptcy_years_ago: float | None
    has_judgments: bool
    has_repossessions: bool
    has_tax_liens: bool
    is_us_citizen: bool
    status: ApplicationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class LoanApplicationDetail(LoanApplicationOut):
    match_results: list["MatchResultOut"] = []


# avoid circular import
from .match_result import MatchResultOut  # noqa: E402
LoanApplicationDetail.model_rebuild()