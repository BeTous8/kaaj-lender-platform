from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import LoanApplication
from app.services.matching import run_matching

router = APIRouter(prefix="/api/underwrite", tags=["underwrite"])


@router.post("/{app_id}")
async def trigger_underwrite(app_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LoanApplication).where(LoanApplication.id == app_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        matches = await run_matching(app_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "application_id": app_id,
        "status": "complete",
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