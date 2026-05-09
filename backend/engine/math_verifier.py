import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor
from typing import Union
import re


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

    @classmethod
    def verify_question_answer(cls, question_text: str, proposed_answer: str) -> bool:
        """Verify that a question's proposed_answer is mathematically correct."""
        if proposed_answer is None:
            return False
        if isinstance(proposed_answer, (int, float)):
            proposed_answer = str(proposed_answer)

        expr_text = cls._extract_expression(question_text)
        if not expr_text:
            return len(str(proposed_answer).strip()) > 0

        try:
            true_expr = cls.parse(expr_text)

            # For algebraic expressions (contain variable symbols like x, y):
            # simplify the expression and compare
            if any(c.isalpha() for c in expr_text if c not in ('e', 'E')):
                simplified = sp.simplify(sp.expand(true_expr))
                clean_ans = cls._clean_answer(proposed_answer)
                try:
                    ans_expr = cls.parse(clean_ans)
                    diff = sp.simplify(simplified - ans_expr)
                    return bool(diff == 0)
                except Exception:
                    return False

            # For numeric expressions: compute and compare
            true_value = sp.N(true_expr)
            clean_ans = cls._clean_answer(proposed_answer)
            ans_expr = cls.parse(clean_ans)
            diff = sp.simplify(true_expr - ans_expr)
            return bool(diff == 0 or abs(float(sp.N(diff))) < 1e-9)
        except Exception:
            return True  # Can't verify — accept as-is

    @staticmethod
    def _extract_expression(text: str) -> str | None:
        """Extract a compute-able math expression from question text."""
        # Clean the text first
        text = text.strip()

        # Pattern 1: 展开并化简 / 化简 / Expand / Simplify + expression
        # e.g. "展开并化简 (x+3)(x-5)"
        match = re.search(r'(展开并化简|化简|Expand|Simplify|展开)[:：]?\s*((?:\([^)]+\)|[-\w\*\^\+])+(?:\s*[-+]\s*(?:\([^)]+\)|[-\w\*\^\+])+)*)', text)
        if match:
            return MathVerifier._normalize_expression(match.group(2).strip())

        # Pattern 2: 计算 / Calculate + pure math expression (no Chinese)
        # e.g. "计算：(-15) + 8 × (-2)" 
        match = re.search(r'(计算|Calculate)[:：]?\s*([-+\d×÷\^\(\)\s\*\w/\.]+)$', text)
        if match:
            expr = match.group(2).strip()
            # Must contain operators to be a real expression
            if re.search(r'[-+*/×÷\^]', expr):
                return MathVerifier._normalize_expression(expr)

        # Pattern 3: LaTeX math
        match = re.search(r'\\[\(\[](.+?)\\[\)\]]', text)
        if match:
            return MathVerifier._normalize_expression(match.group(1))

        # Pattern 4: 解方程 / Solve
        match = re.search(r'(解方程|Solve)[:：]?\s*([\dxX\s=\+\-*/\(\)]+)', text)
        if match:
            return MathVerifier._normalize_expression(match.group(2).strip())

        return None

        # Look for LaTeX-like math: \(...\) or \[...\]
        match = re.search(r'\\[\(\[](.+?)\\[\)\]]', text)
        if match:
            return MathVerifier._normalize_expression(match.group(1))

        # Look for formula pattern: numbers with operators
        match = re.search(r'([-+]?\s*\d+[-\+\*/×÷\^]\s*.+)', text)
        if match:
            return MathVerifier._normalize_expression(match.group(1))

        # Try the whole text as an expression
        cleaned = text.replace(' ', '').replace('？', '').replace('?', '')
        if re.match(r'^[-+\d].*[-+\*/^].*[-+\d]$', cleaned):
            return MathVerifier._normalize_expression(cleaned)

        return None

    @staticmethod
    def _normalize_expression(expr: str) -> str:
        """Normalize Chinese/Unicode math operators to SymPy-compatible."""
        return expr.replace('×', '*').replace('÷', '/').replace('−', '-').replace('²', '**2').replace('³', '**3').replace(' ', '')

    @staticmethod
    def _clean_answer(ans: str) -> str:
        """Clean answer text: remove units, Chinese text, keep only math."""
        # Remove Chinese characters
        ans = re.sub(r'[\u4e00-\u9fff]+', '', ans)
        # Remove degree symbol
        ans = ans.replace('°', '')
        # Normalize operators
        ans = MathVerifier._normalize_expression(ans)
        ans = ans.strip()
        return ans if ans else '0'
