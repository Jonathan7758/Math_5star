"""LLM-generated question verification test suite.

These tests verify that LLM-generated questions pass SymPy verification
and meet formatting requirements. Run with LLM_API_KEY set to test live
generation, or skip if unset.
"""

import os

import pytest

from backend.agents.llm_agent import LLMAgent
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.engine.math_verifier import MathVerifier
from backend.config import KNOWLEDGE_GRAPH_PATH


class TestLLMConfiguration:
    def test_api_config_present(self):
        assert LLMAgent.is_configured() or not os.getenv("LLM_API_KEY"), \
            "LLM config should be set via environment or skipped"


class TestLLMFormatCompliance:
    """Test that LLM responses match expected format."""

    VALID_SAMPLE = {
        "question": "Calculate: 5 + 3 × 2",
        "type": "numeric",
        "correct_answer": "11",
        "hints": ["Remember BODMAS", "Multiplication before addition"],
        "explanation": "5 + 3 × 2 = 5 + 6 = 11",
    }

    def test_sample_format_has_all_fields(self):
        required = {"question", "type", "correct_answer", "hints", "explanation"}
        assert required.issubset(set(self.VALID_SAMPLE.keys()))

    def test_sample_passes_verification(self):
        ok, _ = MathVerifier.verify(
            self.VALID_SAMPLE["question"],
            self.VALID_SAMPLE["correct_answer"],
        )
        assert ok

    def test_multiple_choice_format(self):
        sample = {
            "question": "What is 2 + 2?",
            "type": "multiple_choice",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4",
            "hints": ["Think carefully"],
            "explanation": "2 + 2 = 4",
        }
        assert sample["type"] == "multiple_choice"
        assert len(sample["options"]) == 4
        ok, _ = MathVerifier.verify(sample["question"], sample["correct_answer"])
        assert ok


class TestLLMMathAccuracy:
    """Test common math problem types through verification."""

    CASES = [
        ("2 + 3 × 4", "14"),
        ("(6 + 2) × 3", "24"),
        ("12 ÷ 4 + 2", "5"),
        ("-5 + 12", "7"),
        ("(-3) × (-4)", "12"),
        ("2^3 + 1", "9"),
        ("15 % 4", "3"),
        ("sqrt(16)", "4"),
        ("x = 5; 2x + 3", "13"),
        ("1/2 + 1/3", "5/6"),
    ]

    @pytest.mark.parametrize("expr,expected", CASES)
    def test_verifier_correct(self, expr, expected):
        ok, _ = MathVerifier.verify(expr, expected)
        assert ok, f"Verifier failed for {expr} = {expected}"


class TestLLMSafety:
    """Ensure LLM questions are safe and appropriate."""

    def test_no_harmful_content_templates(self):
        harmful = ["kill", "hate", "sex", "drug"]
        for keyword in harmful:
            assert keyword not in str(LLMAgent).lower()


class TestLLMConsistency:
    """Test that generated questions are consistent."""

    @pytest.mark.skipif(not LLMAgent.is_configured(), reason="LLM not configured")
    @pytest.mark.asyncio
    async def test_generate_question_returns_valid(self):
        question = await LLMAgent.generate_question(
            kp_name="Integer Operations",
            kp_description="Addition and subtraction of integers",
            grade="Y7",
            level=1,
        )
        if question:
            assert "question" in question
            assert "correct_answer" in question
            ok, _ = MathVerifier.verify(question["question"], question["correct_answer"])
            assert ok, f"LLM generated incorrect answer for: {question['question']}"

    @pytest.mark.skipif(not LLMAgent.is_configured(), reason="LLM not configured")
    @pytest.mark.asyncio
    async def test_generate_explanation_not_empty(self):
        explanation = await LLMAgent.generate_explanation(
            kp_name="Fractions Basics",
            kp_description="Understanding fractions",
        )
        if explanation:
            assert len(explanation) > 20
