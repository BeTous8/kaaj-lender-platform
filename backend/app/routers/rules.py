from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import PolicyRule
from app.schemas import PolicyRuleUpdate, PolicyRuleOut

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.put("/{rule_id}", response_model=PolicyRuleOut)
async def update_rule(rule_id: int, payload: PolicyRuleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PolicyRule).where(PolicyRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PolicyRule).where(PolicyRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()