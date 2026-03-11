"""
Seed script: populates all 5 lenders with programs and policy rules.
Run from backend/ directory: python seed.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models import Lender, Program, PolicyRule
from app.models.policy_rule import RuleOperator

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/kaaj_lender"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def rule(field, op, value, hard_stop=False, desc=None):
    return dict(field_name=field, operator=op, value=str(value), is_hard_stop=hard_stop, description=desc)


STEARNS_EXCLUDED_INDUSTRIES = (
    "Gaming/Gambling,Hazmat,Oil & Gas,MSBs,Adult Entertainment,"
    "Real Estate,OTR,Restaurants,Car Wash,Beauty/Tanning Salons,"
    "Tattoo/Piercing,Weapons/Firearms"
)

APEX_EXCLUDED_STATES = "CA,NV,ND,VT"
APEX_EXCLUDED_EQUIPMENT = (
    "Aircrafts,Boats,ATMs,Cannabis,Copiers,Electric Vehicles,"
    "Equipment over 15 years old,Trucking,Nail Salons"
)

SEED_DATA = [
    # ─────────────────────────────────────────────
    # 1. STEARNS BANK
    # ─────────────────────────────────────────────
    {
        "name": "Stearns Bank",
        "slug": "stearns-bank",
        "is_active": True,
        "notes": "Standard FICO/PayNet tiers plus Corp-Only tiers. No BK < 7 years.",
        "programs": [
            {
                "name": "Tier 1",
                "priority": 1,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 725, desc="Min FICO 725"),
                    rule("paynet_score", RuleOperator.gte, 685, desc="Min PayNet 685"),
                    rule("years_in_business", RuleOperator.gte, 3, desc="Min 3 years in business"),
                    rule("industry", RuleOperator.not_in, STEARNS_EXCLUDED_INDUSTRIES, hard_stop=True, desc="Excluded industries"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No active bankruptcy"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 7, desc="BK must be 7+ years ago if applicable"),
                ],
            },
            {
                "name": "Tier 2",
                "priority": 2,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 710, desc="Min FICO 710"),
                    rule("paynet_score", RuleOperator.gte, 675, desc="Min PayNet 675"),
                    rule("years_in_business", RuleOperator.gte, 3, desc="Min 3 years in business"),
                    rule("industry", RuleOperator.not_in, STEARNS_EXCLUDED_INDUSTRIES, hard_stop=True, desc="Excluded industries"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No active bankruptcy"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 7, desc="BK must be 7+ years ago if applicable"),
                ],
            },
            {
                "name": "Tier 3",
                "priority": 3,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 700, desc="Min FICO 700"),
                    rule("paynet_score", RuleOperator.gte, 665, desc="Min PayNet 665"),
                    rule("years_in_business", RuleOperator.gte, 2, desc="Min 2 years in business"),
                    rule("industry", RuleOperator.not_in, STEARNS_EXCLUDED_INDUSTRIES, hard_stop=True, desc="Excluded industries"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No active bankruptcy"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 7, desc="BK must be 7+ years ago if applicable"),
                ],
            },
            {
                "name": "Corp Only Tier 1",
                "priority": 4,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 735, desc="Min FICO 735"),
                    rule("years_in_business", RuleOperator.gte, 5, desc="Min 5 years in business"),
                    rule("industry", RuleOperator.not_in, STEARNS_EXCLUDED_INDUSTRIES, hard_stop=True, desc="Excluded industries"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No active bankruptcy"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 7, desc="BK must be 7+ years ago if applicable"),
                ],
            },
            {
                "name": "Corp Only Tier 2",
                "priority": 5,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 720, desc="Min FICO 720"),
                    rule("years_in_business", RuleOperator.gte, 3, desc="Min 3 years in business"),
                    rule("industry", RuleOperator.not_in, STEARNS_EXCLUDED_INDUSTRIES, hard_stop=True, desc="Excluded industries"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No active bankruptcy"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 7, desc="BK must be 7+ years ago if applicable"),
                ],
            },
            {
                "name": "Corp Only Tier 3",
                "priority": 6,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 710, desc="Min FICO 710"),
                    rule("years_in_business", RuleOperator.gte, 2, desc="Min 2 years in business"),
                    rule("industry", RuleOperator.not_in, STEARNS_EXCLUDED_INDUSTRIES, hard_stop=True, desc="Excluded industries"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No active bankruptcy"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 7, desc="BK must be 7+ years ago if applicable"),
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # 2. APEX COMMERCIAL CAPITAL
    # ─────────────────────────────────────────────
    {
        "name": "Apex Commercial Capital",
        "slug": "apex-commercial-capital",
        "is_active": True,
        "notes": "Does not lend in CA, NV, ND, VT. Excluded equipment types apply to all programs.",
        "programs": [
            {
                "name": "A+ Rate",
                "priority": 1,
                "rules": [
                    rule("state", RuleOperator.not_in, APEX_EXCLUDED_STATES, hard_stop=True, desc="Does not lend in CA, NV, ND, VT"),
                    rule("fico_score", RuleOperator.gte, 720, desc="Min FICO 720"),
                    rule("paynet_score", RuleOperator.gte, 670, desc="Min PayNet 670"),
                    rule("years_in_business", RuleOperator.gte, 5, desc="Min 5 years in business"),
                    rule("loan_amount", RuleOperator.lte, 500000, desc="Max loan $500,000"),
                    rule("equipment_type", RuleOperator.not_in, APEX_EXCLUDED_EQUIPMENT, hard_stop=True, desc="Excluded equipment types"),
                ],
            },
            {
                "name": "A Rate",
                "priority": 2,
                "rules": [
                    rule("state", RuleOperator.not_in, APEX_EXCLUDED_STATES, hard_stop=True, desc="Does not lend in CA, NV, ND, VT"),
                    rule("fico_score", RuleOperator.gte, 700, desc="Min FICO 700"),
                    rule("paynet_score", RuleOperator.gte, 660, desc="Min PayNet 660"),
                    rule("years_in_business", RuleOperator.gte, 5, desc="Min 5 years in business"),
                    rule("loan_amount", RuleOperator.lte, 500000, desc="Max loan $500,000"),
                    rule("equipment_type", RuleOperator.not_in, APEX_EXCLUDED_EQUIPMENT, hard_stop=True, desc="Excluded equipment types"),
                ],
            },
            {
                "name": "B Rate",
                "priority": 3,
                "rules": [
                    rule("state", RuleOperator.not_in, APEX_EXCLUDED_STATES, hard_stop=True, desc="Does not lend in CA, NV, ND, VT"),
                    rule("fico_score", RuleOperator.gte, 670, desc="Min FICO 670"),
                    rule("paynet_score", RuleOperator.gte, 650, desc="Min PayNet 650"),
                    rule("years_in_business", RuleOperator.gte, 3, desc="Min 3 years in business"),
                    rule("loan_amount", RuleOperator.lte, 250000, desc="Max loan $250,000"),
                    rule("equipment_type", RuleOperator.not_in, APEX_EXCLUDED_EQUIPMENT, hard_stop=True, desc="Excluded equipment types"),
                ],
            },
            {
                "name": "C Rate",
                "priority": 4,
                "rules": [
                    rule("state", RuleOperator.not_in, APEX_EXCLUDED_STATES, hard_stop=True, desc="Does not lend in CA, NV, ND, VT"),
                    rule("fico_score", RuleOperator.gte, 640, desc="Min FICO 640"),
                    rule("paynet_score", RuleOperator.gte, 640, desc="Min PayNet 640"),
                    rule("years_in_business", RuleOperator.gte, 2, desc="Min 2 years in business"),
                    rule("loan_amount", RuleOperator.lte, 100000, desc="Max loan $100,000"),
                    rule("equipment_type", RuleOperator.not_in, APEX_EXCLUDED_EQUIPMENT, hard_stop=True, desc="Excluded equipment types"),
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # 3. ADVANTAGE+ FINANCING
    # ─────────────────────────────────────────────
    {
        "name": "Advantage+ Financing",
        "slug": "advantage-plus-financing",
        "is_active": True,
        "notes": "Non-trucking only. Loan range $10k-$75k. US citizens only. Hard stops: no BK, judgments, repossessions, tax liens.",
        "programs": [
            {
                "name": "Standard",
                "priority": 1,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 680, desc="Min FICO 680"),
                    rule("years_in_business", RuleOperator.gte, 2, desc="Min 2 years in business"),
                    rule("equipment_type", RuleOperator.not_in, "Trucking,OTR", hard_stop=True, desc="Non-trucking only"),
                    rule("loan_amount", RuleOperator.gte, 10000, desc="Min loan $10,000"),
                    rule("loan_amount", RuleOperator.lte, 75000, desc="Max loan $75,000"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No bankruptcies"),
                    rule("has_judgments", RuleOperator.equals, "False", hard_stop=True, desc="No judgments"),
                    rule("has_repossessions", RuleOperator.equals, "False", hard_stop=True, desc="No repossessions"),
                    rule("has_tax_liens", RuleOperator.equals, "False", hard_stop=True, desc="No tax liens"),
                    rule("is_us_citizen", RuleOperator.equals, "True", hard_stop=True, desc="US citizens only"),
                ],
            },
            {
                "name": "Startup",
                "priority": 2,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 700, desc="Min FICO 700 for startups"),
                    rule("is_startup", RuleOperator.equals, "True", desc="Startup program (TIB < 2 years)"),
                    rule("equipment_type", RuleOperator.not_in, "Trucking,OTR", hard_stop=True, desc="Non-trucking only"),
                    rule("loan_amount", RuleOperator.gte, 10000, desc="Min loan $10,000"),
                    rule("loan_amount", RuleOperator.lte, 75000, desc="Max loan $75,000"),
                    rule("has_bankruptcy", RuleOperator.equals, "False", hard_stop=True, desc="No bankruptcies"),
                    rule("has_judgments", RuleOperator.equals, "False", hard_stop=True, desc="No judgments"),
                    rule("has_repossessions", RuleOperator.equals, "False", hard_stop=True, desc="No repossessions"),
                    rule("has_tax_liens", RuleOperator.equals, "False", hard_stop=True, desc="No tax liens"),
                    rule("is_us_citizen", RuleOperator.equals, "True", hard_stop=True, desc="US citizens only"),
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # 4. FALCON EQUIPMENT FINANCE
    # ─────────────────────────────────────────────
    {
        "name": "Falcon Equipment Finance",
        "slug": "falcon-equipment-finance",
        "is_active": True,
        "notes": "Min loan $15k. BK only if 15+ years discharged.",
        "programs": [
            {
                "name": "A Credit",
                "priority": 1,
                "rules": [
                    rule("paynet_score", RuleOperator.gte, 660, desc="Min PayNet 660"),
                    rule("years_in_business", RuleOperator.gte, 3, desc="Min 3 years in business"),
                    rule("loan_amount", RuleOperator.gte, 15000, desc="Min loan $15,000"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 15, desc="BK must be 15+ years discharged if applicable"),
                ],
            },
            {
                "name": "Trucking Special",
                "priority": 2,
                "rules": [
                    rule("fico_score", RuleOperator.gte, 700, desc="Min FICO 700"),
                    rule("paynet_score", RuleOperator.gte, 680, desc="Min PayNet 680"),
                    rule("years_in_business", RuleOperator.gte, 5, desc="Min 5 years in business"),
                    rule("equipment_type", RuleOperator.in_, "Trucking,OTR,Semi-Truck,Commercial Truck", desc="Trucking equipment required"),
                    rule("loan_amount", RuleOperator.gte, 15000, desc="Min loan $15,000"),
                    rule("bankruptcy_years_ago", RuleOperator.gte, 15, desc="BK must be 15+ years discharged if applicable"),
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────
    # 5. CITIZENS BANK
    # ─────────────────────────────────────────────
    {
        "name": "Citizens Bank",
        "slug": "citizens-bank",
        "is_active": True,
        "notes": "Uses TransUnion score (not FICO). Does not lend in CA. US citizens only. No cannabis.",
        "programs": [
            {
                "name": "Tier 1 - App Only up to $75k",
                "priority": 1,
                "rules": [
                    rule("state", RuleOperator.not_in, "CA", hard_stop=True, desc="Does not lend in CA"),
                    rule("transunion_score", RuleOperator.gte, 700, desc="Min TransUnion 700"),
                    rule("years_in_business", RuleOperator.gte, 2, desc="Min 2 years in business"),
                    rule("loan_amount", RuleOperator.lte, 75000, desc="App-only max $75,000"),
                    rule("equipment_type", RuleOperator.not_in, "Cannabis", hard_stop=True, desc="No cannabis"),
                    rule("is_us_citizen", RuleOperator.equals, "True", hard_stop=True, desc="US citizens only"),
                ],
            },
            {
                "name": "Tier 2 - Startup App Only up to $50k",
                "priority": 2,
                "rules": [
                    rule("state", RuleOperator.not_in, "CA", hard_stop=True, desc="Does not lend in CA"),
                    rule("transunion_score", RuleOperator.gte, 700, desc="Min TransUnion 700"),
                    rule("years_in_business", RuleOperator.gte, 2, desc="Min 2 years in business"),
                    rule("is_startup", RuleOperator.equals, "True", desc="Startup program"),
                    rule("loan_amount", RuleOperator.lte, 50000, desc="App-only max $50,000"),
                    rule("equipment_type", RuleOperator.not_in, "Cannabis", hard_stop=True, desc="No cannabis"),
                    rule("is_us_citizen", RuleOperator.equals, "True", hard_stop=True, desc="US citizens only"),
                ],
            },
        ],
    },
]


async def seed():
    async with AsyncSessionLocal() as session:
        for lender_data in SEED_DATA:
            programs_data = lender_data.pop("programs")
            lender = Lender(**lender_data)
            session.add(lender)
            await session.flush()

            for prog_data in programs_data:
                rules_data = prog_data.pop("rules")
                program = Program(lender_id=lender.id, **prog_data)
                session.add(program)
                await session.flush()

                for r in rules_data:
                    policy_rule = PolicyRule(program_id=program.id, **r)
                    session.add(policy_rule)

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())