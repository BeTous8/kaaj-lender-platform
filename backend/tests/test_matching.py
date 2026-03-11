"""Unit tests for the matching engine — no database required."""
import pytest
from unittest.mock import MagicMock

from app.models.policy_rule import RuleOperator
from app.services.matching import evaluate_rule, evaluate_program


def make_rule(field_name, operator, value, is_hard_stop=False, rule_id=1):
    rule = MagicMock()
    rule.id = rule_id
    rule.field_name = field_name
    rule.operator = operator
    rule.value = value
    rule.is_hard_stop = is_hard_stop
    return rule


def make_application(**kwargs):
    app = MagicMock()
    # Set sensible defaults for all fields
    defaults = dict(
        fico_score=700,
        paynet_score=60,
        transunion_score=680,
        loan_amount=50000.0,
        years_in_business=5.0,
        annual_revenue=500000.0,
        state="TX",
        industry="manufacturing",
        equipment_type="trailer",
        equipment_year=2020,
        equipment_mileage=50000,
        is_startup=False,
        has_bankruptcy=False,
        bankruptcy_years_ago=None,
        has_judgments=False,
        has_repossessions=False,
        has_tax_liens=False,
        is_us_citizen=True,
    )
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(app, k, v)

    # getattr on MagicMock for unknown fields returns a new Mock;
    # we need it to return None for fields that don't exist on the app.
    # Override __getattr__ isn't easy with MagicMock, so we'll rely on
    # explicit field setting which is sufficient for these tests.
    return app


# ---------------------------------------------------------------------------
# evaluate_rule — operator tests
# ---------------------------------------------------------------------------

class TestEvaluateRuleGte:
    def test_passes_when_equal(self):
        rule = make_rule("fico_score", RuleOperator.gte, "700")
        app = make_application(fico_score=700)
        passed, explanation = evaluate_rule(rule, app)
        assert passed is True
        assert "700" in explanation

    def test_passes_when_above(self):
        rule = make_rule("fico_score", RuleOperator.gte, "700")
        app = make_application(fico_score=750)
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_when_below(self):
        rule = make_rule("fico_score", RuleOperator.gte, "700")
        app = make_application(fico_score=640)
        passed, explanation = evaluate_rule(rule, app)
        assert passed is False
        assert "640" in explanation
        assert "700" in explanation


class TestEvaluateRuleLte:
    def test_passes_when_equal(self):
        rule = make_rule("loan_amount", RuleOperator.lte, "75000")
        app = make_application(loan_amount=75000.0)
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_when_above(self):
        rule = make_rule("loan_amount", RuleOperator.lte, "75000")
        app = make_application(loan_amount=100000.0)
        passed, explanation = evaluate_rule(rule, app)
        assert passed is False
        assert "exceeds" in explanation.lower() or "maximum" in explanation.lower()


class TestEvaluateRuleGt:
    def test_passes_when_above(self):
        rule = make_rule("years_in_business", RuleOperator.gt, "2")
        app = make_application(years_in_business=3.0)
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_when_equal(self):
        rule = make_rule("years_in_business", RuleOperator.gt, "2")
        app = make_application(years_in_business=2.0)
        passed, _ = evaluate_rule(rule, app)
        assert passed is False


class TestEvaluateRuleLt:
    def test_passes_when_below(self):
        rule = make_rule("equipment_mileage", RuleOperator.lt, "100000")
        app = make_application(equipment_mileage=80000)
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_when_equal(self):
        rule = make_rule("equipment_mileage", RuleOperator.lt, "100000")
        app = make_application(equipment_mileage=100000)
        passed, _ = evaluate_rule(rule, app)
        assert passed is False


class TestEvaluateRuleEquals:
    def test_passes_case_insensitive(self):
        rule = make_rule("state", RuleOperator.equals, "TX")
        app = make_application(state="tx")
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_different_value(self):
        rule = make_rule("state", RuleOperator.equals, "TX")
        app = make_application(state="CA")
        passed, explanation = evaluate_rule(rule, app)
        assert passed is False
        assert "CA" in explanation


class TestEvaluateRuleNotIn:
    def test_passes_when_not_in_list(self):
        rule = make_rule("state", RuleOperator.not_in, "CA,NV,ND,VT")
        app = make_application(state="TX")
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_when_in_list(self):
        rule = make_rule("state", RuleOperator.not_in, "CA,NV,ND,VT")
        app = make_application(state="CA")
        passed, explanation = evaluate_rule(rule, app)
        assert passed is False
        assert "excluded" in explanation.lower() or "not allowed" in explanation.lower()

    def test_handles_spaces_around_commas(self):
        rule = make_rule("state", RuleOperator.not_in, "CA, NV, ND, VT")
        app = make_application(state="NV")
        passed, _ = evaluate_rule(rule, app)
        assert passed is False


class TestEvaluateRuleIn:
    def test_passes_when_in_list(self):
        rule = make_rule("industry", RuleOperator.in_, "manufacturing,construction,healthcare")
        app = make_application(industry="manufacturing")
        passed, _ = evaluate_rule(rule, app)
        assert passed is True

    def test_fails_when_not_in_list(self):
        rule = make_rule("industry", RuleOperator.in_, "manufacturing,construction,healthcare")
        app = make_application(industry="retail")
        passed, explanation = evaluate_rule(rule, app)
        assert passed is False
        assert "not in allowed list" in explanation.lower()


class TestEvaluateRuleNoneValue:
    def test_returns_false_with_message_when_field_is_none(self):
        rule = make_rule("fico_score", RuleOperator.gte, "700")
        app = make_application(fico_score=None)
        passed, explanation = evaluate_rule(rule, app)
        assert passed is False
        assert "fico_score" in explanation
        assert "not provided" in explanation


# ---------------------------------------------------------------------------
# evaluate_program — eligibility and fit score
# ---------------------------------------------------------------------------

class TestEvaluateProgram:
    def _make_program(self, rules):
        program = MagicMock()
        program.policy_rules = rules
        return program

    def test_all_pass_returns_eligible_score_100(self):
        rules = [
            make_rule("fico_score", RuleOperator.gte, "700", rule_id=1),
            make_rule("state", RuleOperator.not_in, "CA,NV", rule_id=2),
        ]
        program = self._make_program(rules)
        app = make_application(fico_score=750, state="TX")

        result = evaluate_program(program, app)

        assert result["is_eligible"] is True
        assert result["fit_score"] == 100
        assert len(result["rule_results"]) == 2
        assert all(r["passed"] for r in result["rule_results"])

    def test_hard_stop_failure_makes_ineligible(self):
        rules = [
            make_rule("fico_score", RuleOperator.gte, "700", is_hard_stop=True, rule_id=1),
        ]
        program = self._make_program(rules)
        app = make_application(fico_score=600)

        result = evaluate_program(program, app)

        assert result["is_eligible"] is False
        assert result["rule_results"][0]["passed"] is False

    def test_hard_stop_failure_subtracts_40_points(self):
        rules = [
            make_rule("fico_score", RuleOperator.gte, "700", is_hard_stop=True, rule_id=1),
        ]
        program = self._make_program(rules)
        app = make_application(fico_score=600)

        result = evaluate_program(program, app)

        assert result["fit_score"] == 60

    def test_soft_failure_subtracts_10_points(self):
        rules = [
            make_rule("years_in_business", RuleOperator.gte, "5", is_hard_stop=False, rule_id=1),
        ]
        program = self._make_program(rules)
        app = make_application(years_in_business=2.0)

        result = evaluate_program(program, app)

        assert result["is_eligible"] is True
        assert result["fit_score"] == 90

    def test_soft_failure_does_not_make_ineligible(self):
        rules = [
            make_rule("years_in_business", RuleOperator.gte, "5", is_hard_stop=False, rule_id=1),
        ]
        program = self._make_program(rules)
        app = make_application(years_in_business=2.0)

        result = evaluate_program(program, app)

        assert result["is_eligible"] is True

    def test_multiple_failures_stack(self):
        rules = [
            make_rule("fico_score", RuleOperator.gte, "700", is_hard_stop=True, rule_id=1),
            make_rule("years_in_business", RuleOperator.gte, "5", is_hard_stop=False, rule_id=2),
            make_rule("loan_amount", RuleOperator.lte, "75000", is_hard_stop=False, rule_id=3),
        ]
        program = self._make_program(rules)
        # Fail all three
        app = make_application(fico_score=600, years_in_business=2.0, loan_amount=100000.0)

        result = evaluate_program(program, app)

        assert result["is_eligible"] is False
        # 100 - 40 (hard_stop) - 10 - 10 = 40
        assert result["fit_score"] == 40

    def test_score_floor_is_zero(self):
        rules = [
            make_rule("fico_score", RuleOperator.gte, "700", is_hard_stop=True, rule_id=i)
            for i in range(1, 5)  # 4 hard stops = -160 points
        ]
        program = self._make_program(rules)
        app = make_application(fico_score=500)

        result = evaluate_program(program, app)

        assert result["fit_score"] == 0

    def test_rule_results_contain_required_keys(self):
        rules = [make_rule("fico_score", RuleOperator.gte, "700", rule_id=1)]
        program = self._make_program(rules)
        app = make_application(fico_score=750)

        result = evaluate_program(program, app)

        rr = result["rule_results"][0]
        assert "rule_id" in rr
        assert "passed" in rr
        assert "actual_value" in rr
        assert "required_value" in rr
        assert "explanation" in rr
