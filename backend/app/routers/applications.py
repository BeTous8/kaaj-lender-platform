from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models import LoanApplication, MatchResult
from app.schemas import LoanApplicationCreate, LoanApplicationOut, LoanApplicationDetail

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[LoanApplicationOut])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoanApplication).order_by(LoanApplication.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=LoanApplicationOut, status_code=201)
async def create_application(payload: LoanApplicationCreate, db: AsyncSession = Depends(get_db)):
    application = LoanApplication(**payload.model_dump())
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/{app_id}", response_model=LoanApplicationDetail)
async def get_application(app_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoanApplication)
        .options(
            selectinload(LoanApplication.match_results).selectinload(MatchResult.rule_evaluations)
        )
        .where(LoanApplication.id == app_id)
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.get("/{app_id}/results")
async def get_application_results(app_id: int, db: AsyncSession = Depends(get_db)):
    app_result = await db.execute(
        select(LoanApplication).where(LoanApplication.id == app_id)
    )
    application = app_result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    from app.models import Lender, Program
    from sqlalchemy.orm import selectinload as sil

    matches_result = await db.execute(
        select(MatchResult)
        .where(MatchResult.application_id == app_id)
        .options(
            sil(MatchResult.lender),
            sil(MatchResult.program),
            sil(MatchResult.rule_evaluations),
        )
        .order_by(MatchResult.fit_score.desc())
    )
    matches = matches_result.scalars().all()

    return {
        "application_id": app_id,
        "status": application.status,
        "match_count": len(matches),
        "results": [
            {
                "lender_id": m.lender_id,
                "lender_name": m.lender.name,
                "program_id": m.program_id,
                "program_name": m.program.name,
                "is_eligible": m.is_eligible,
                "fit_score": m.fit_score,
                "rule_evaluations": [
                    {
                        "rule_id": e.policy_rule_id,
                        "passed": e.passed,
                        "actual_value": e.actual_value,
                        "required_value": e.required_value,
                        "explanation": e.explanation,
                    }
                    for e in m.rule_evaluations
                ],
            }
            for m in matches
        ],
    }