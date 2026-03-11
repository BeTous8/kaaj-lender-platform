from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models import Program, PolicyRule
from app.schemas import ProgramCreate, ProgramOut, PolicyRuleCreate, PolicyRuleOut

router = APIRouter(prefix="/api/programs", tags=["programs"])


@router.post("", response_model=ProgramOut, status_code=status.HTTP_201_CREATED)
async def create_program(payload: ProgramCreate, db: AsyncSession = Depends(get_db)):
    program = Program(**payload.model_dump())
    db.add(program)
    await db.commit()
    result = await db.execute(
        select(Program)
        .options(selectinload(Program.policy_rules))
        .where(Program.id == program.id)
    )
    return result.scalar_one()


@router.post("/{program_id}/rules", response_model=PolicyRuleOut, status_code=status.HTTP_201_CREATED)
async def add_rule(program_id: int, payload: PolicyRuleCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    rule = PolicyRule(program_id=program_id, **payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule