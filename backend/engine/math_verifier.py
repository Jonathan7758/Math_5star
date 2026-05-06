import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor
from typing import Union


class MathVerifier:
    TRANSFORMATIONS = standard_transformations + (implicit_multiplication, convert_xor)

    @staticmethod
    def parse(expr: str) -> sp.Basic:
        return parse_expr(expr, transformations=MathVerifier.TRANSFORMATIONS)

    @classmethod
    def is_equivalent(cls, student_answer: str, correct_answer: str) -> bool:
        try:
            a = cls.parse(student_answer)
            b = cls.parse(correct_answer)
            diff = sp.simplify(a - b)
            return bool(diff.is_zero)
        except Exception:
            return False

    @classmethod
    def is_numeric_equal(cls, student_answer: str, correct_answer: str) -> bool:
        try:
            a = float(sp.N(cls.parse(student_answer)))
            b = float(sp.N(cls.parse(correct_answer)))
            return abs(a - b) < 1e-9
        except Exception:
            return False

    @classmethod
    def verify(cls, student_answer: str, correct_answer: str) -> dict:
        try:
            equivalent = cls.is_equivalent(student_answer, correct_answer)
            numeric = cls.is_numeric_equal(student_answer, correct_answer)
            return {
                "is_correct": equivalent or numeric,
                "method": "equivalent" if equivalent else ("numeric" if numeric else "none"),
            }
        except Exception as e:
            return {"is_correct": False, "error": str(e)}

    @classmethod
    def solve_equation(cls, equation: str, variable: str = "x") -> list[str]:
        try:
            left, right = equation.split("=")
            expr = cls.parse(f"({left}) - ({right})")
            solutions = sp.solve(expr, sp.Symbol(variable))
            return [str(s) for s in solutions]
        except Exception as e:
            return []

    @classmethod
    def simplify(cls, expr: str) -> str:
        try:
            parsed = cls.parse(expr)
            return str(sp.simplify(parsed))
        except Exception:
            return expr
