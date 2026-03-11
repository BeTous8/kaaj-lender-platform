from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Lender,
    LoanApplication,
    ApplicationStatus,
    MatchResult,
    RuleEvaluation,
)
from app.models.policy_rule import PolicyRule, RuleOperator
from app.models.program import Program


def evaluate_rule(rule: PolicyRule, application: LoanApplication) -> tuple[bool, str]:
    actual = getattr(application, rule.field_name, None)
    required = rule.value
    field = rule.field_name

    if actual is None:
        return False, f"field '{field}' was not provided"

    op = rule.operator

    if op in (RuleOperator.gte, RuleOperator.lte, RuleOperator.gt, RuleOperator.lt):
        try:
            actual_f = float(actual)
            required_f = float(required)
        except (TypeError, ValueError):
            return False, f"{field} value '{actual}' or required '{required}' is not numeric"

        if op == RuleOperator.gte:
            passed = actual_f >= required_f
            explanation = (
                f"{field} of {actual_f} meets minimum of {required_f}"
                if passed
                else f"{field} of {actual_f} does not meet minimum of {required_f}"
            )
        elif op == RuleOperator.lte:
            passed = actual_f <= required_f
            explanation = (
                f"{field} of {actual_f} meets maximum of {required_f}"
                if passed
                else f"{field} of {actual_f} exceeds maximum of {required_f}"
            )
        elif op == RuleOperator.gt:
            passed = actual_f > required_f
            explanation = (
                f"{field} of {actual_f} is above {required_f}"
                if passed
                else f"{field} of {actual_f} must be greater than {required_f}"
            )
        else:  # lt
            passed = actual_f < required_f
            explanation = (
                f"{field} of {actual_f} is below {required_f}"
                if passed
                else f"{field} of {actual_f} must be less than {required_f}"
            )
        return passed, explanation

    if op == RuleOperator.equals:
        passed = str(actual).lower() == required.lower()
        explanation = (
            f"{field} matches required value '{required}'"
            if passed
            else f"{field} of '{actual}' does not equal required '{required}'"
        )
        return passed, explanation

    if op == RuleOperator.not_in:
        options = [v.strip() for v in required.split(",")]
        passed = str(actual) not in options
        explanation = (
            f"{field} of '{actual}' is not in excluded list"
            if passed
            else f"{field} of '{actual}' is excluded (not allowed: {required})"
        )
        return passed, explanation

    if op == RuleOperator.in_:
        options = [v.strip() for v in required.split(",")]
        passed = str(actual) in options
        explanation = (
            f"{field} of '{actual}' is in allowed list"
            if passed
            else f"{field} of '{actual}' is not in allowed list ({required})"
        )
        return passed, explanation

    return False, f"unknown operator '{op}'"


def evaluate_program(program: Program, application: LoanApplication) -> dict:
    rule_results = []
    score = 100
    is_eligible = True

    for rule in program.policy_rules:
        passed, explanation = evaluate_rule(rule, application)
        actual = getattr(application, rule.field_name, None)

        rule_results.append(
            {
                "rule_id": rule.id,
                "passed": passed,
                "actual_value": str(actual) if actual is not None else None,
                "required_value": rule.value,
                "explanation": explanation,
            }
        )

        if not passed:
            if rule.is_hard_stop:
                score -= 40
                is_eligible = False
            else:
                score -= 10

    fit_score = max(0, score)

    return {
        "is_eligible": is_eligible,
        "fit_score": fit_score,
        "rule_results": rule_results,
    }


async def run_matching(app_id: int, db: AsyncSession) -> list[MatchResult]:
    # Fetch application
    app_result = await db.execute(
        select(LoanApplication).where(LoanApplication.id == app_id)
    )
    application = app_result.scalar_one_or_none()
    if not application:
        raise ValueError(f"Application {app_id} not found")

    # Fetch active lenders with programs and rules (avoid N+1)
    lenders_result = await db.execute(
        select(Lender)
        .where(Lender.is_active == True)  # noqa: E712
        .options(
            selectinload(Lender.programs).selectinload(Program.policy_rules)
        )
    )
    lenders = lenders_result.scalars().all()

    # Delete any existing match results for this application
    existing_result = await db.execute(
        select(MatchResult).where(MatchResult.application_id == app_id)
    )
    for old_match in existing_result.scalars().all():
        await db.delete(old_match)
    await db.flush()

    saved_matches: list[MatchResult] = []

    for lender in lenders:
        active_programs = sorted(
            [p for p in lender.programs if p.is_active],
            key=lambda p: p.priority,
        )
        if not active_programs:
            continue

        # Evaluate all programs, pick the best fit
        best_eval = None
        best_program = None
        for program in active_programs:
            eval_result = evaluate_program(program, application)
            if best_eval is None or eval_result["fit_score"] > best_eval["fit_score"]:
                best_eval = eval_result
                best_program = program

        if best_program is None or best_eval is None:
            continue

        match = MatchResult(
            application_id=app_id,
            lender_id=lender.id,
            program_id=best_program.id,
            is_eligible=best_eval["is_eligible"],
            fit_score=best_eval["fit_score"],
        )
        db.add(match)
        await db.flush()  # get match.id

        for rule_result in best_eval["rule_results"]:
            evaluation = RuleEvaluation(
                match_result_id=match.id,
                policy_rule_id=rule_result["rule_id"],
                passed=rule_result["passed"],
                actual_value=rule_result["actual_value"],
                required_value=rule_result["required_value"],
                explanation=rule_result["explanation"],
            )
            db.add(evaluation)

        saved_matches.append(match)

    application.status = ApplicationStatus.complete
    await db.commit()

    # Reload matches with evaluations
    reloaded = await db.execute(
        select(MatchResult)
        .where(MatchResult.application_id == app_id)
        .options(
            selectinload(MatchResult.rule_evaluations),
            selectinload(MatchResult.lender),
            selectinload(MatchResult.program),
        )
        .order_by(MatchResult.fit_score.desc())
    )
    return list(reloaded.scalars().all())