from pydantic import BaseModel
from .program import ProgramOut


class LenderCreate(BaseModel):
    name: str
    slug: str
    is_active: bool = True
    notes: str | None = None


class LenderUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    is_active: bool | None = None
    notes: str | None = None


class LenderOut(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    notes: str | None

    model_config = {"from_attributes": True}


class LenderDetail(LenderOut):
    programs: list[ProgramOut] = []