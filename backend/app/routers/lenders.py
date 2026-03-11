from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models import Lender, Program, PolicyRule
from app.schemas import LenderCreate, LenderUpdate, LenderOut, LenderDetail, ProgramCreate, ProgramOut, PolicyRuleCreate, PolicyRuleUpdate, PolicyRuleOut

router = APIRouter(prefix="/api/lenders", tags=["lenders"])


@router.get("", response_model=list[LenderDetail])
async def list_lenders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lender)
        .options(
            selectinload(Lender.programs).selectinload(Program.policy_rules)
        )
        .order_by(Lender.id)
    )
    return result.scalars().all()


@router.get("/{lender_id}", response_model=LenderDetail)
async def get_lender(lender_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lender)
        .options(
            selectinload(Lender.programs).selectinload(Program.policy_rules)
        )
        .where(Lender.id == lender_id)
    )
    lender = result.scalar_one_or_none()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    return lender


@router.post("", response_model=LenderOut, status_code=status.HTTP_201_CREATED)
async def create_lender(payload: LenderCreate, db: AsyncSession = Depends(get_db)):
    lender = Lender(**payload.model_dump())
    db.add(lender)
    await db.commit()
    await db.refresh(lender)
    return lender


@router.put("/{lender_id}", response_model=LenderOut)
async def update_lender(lender_id: int, payload: LenderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lender).where(Lender.id == lender_id))
    lender = result.scalar_one_or_none()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lender, field, value)
    await db.commit()
    await db.refresh(lender)
    return lender