import pytest
from backend.engine.math_verifier import MathVerifier


class TestMathVerifier:
    def test_numeric_equality(self):
        assert MathVerifier.is_numeric_equal("3+4", "7")

    def test_algebraic_equality(self):
        assert MathVerifier.is_equivalent("x^2", "x*x")

    def test_fraction_equality(self):
        assert MathVerifier.is_equivalent("1/2", "2/4")

    def test_equivalent_forms(self):
        assert MathVerifier.is_equivalent("sqrt(4)", "2")

    def test_incorrect_answer(self):
        assert not MathVerifier.is_equivalent("3+4", "8")

    def test_verify_correct(self):
        result = MathVerifier.verify("5", "5")
        assert result["is_correct"]

    def test_verify_equivalent(self):
        result = MathVerifier.verify("0.5", "1/2")
        assert result["is_correct"]

    def test_verify_incorrect(self):
        result = MathVerifier.verify("7", "8")
        assert not result["is_correct"]

    def test_simplify(self):
        result = MathVerifier.simplify("x + x")
        assert result == "2*x"

    def test_parse_invalid_input(self):
        result = MathVerifier.verify("!!!", "5")
        assert not result["is_correct"]

    def test_solve_equation(self):
        solutions = MathVerifier.solve_equation("x + 3 = 7")
        assert len(solutions) > 0
        assert "4" in solutions

    def test_solve_equation_no_solution(self):
        solutions = MathVerifier.solve_equation("x = x + 1")
        assert solutions == []

    def test_complex_expression(self):
        result = MathVerifier.is_equivalent("(x+1)*(x-1)", "x^2 - 1")
        assert result
