import json
import os

import httpx

from backend.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from backend.engine.math_verifier import MathVerifier


class LLMAgent:
    """Generate quiz questions and explanations using DeepSeek API.

    All generated math answers are verified through SymPy before acceptance.
    """

    @staticmethod
    async def generate_question(kp_name: str, kp_description: str, grade: str, level: int = 1) -> dict | None:
        """Generate a new quiz question for a given knowledge point."""
        if not LLM_API_KEY:
            return None

        level_desc = "basic single-step" if level == 1 else "moderate multi-step"
        prompt = f"""Generate a math quiz question for a {grade} student about: {kp_name}.
Topic description: {kp_description}
Difficulty: {level_desc} (level {level})

Return ONLY valid JSON in this exact format:
{{
  "question": "<math question in Chinese>",
  "type": "multiple_choice" or "numeric",
  "options": ["A", "B", "C", "D"] (only if type is multiple_choice, 4 options),
  "correct_answer": "<answer>",
  "hints": ["<hint 1 - general>", "<hint 2 - more specific>"],
  "explanation": "<step-by-step explanation in Chinese>"
}}

Important rules:
- The question must be solvable by a {grade} student
- For numeric type: correct_answer must be a number or simple fraction
- For multiple_choice: exactly 4 options, one correct
- All text must be in Chinese
- Use integer or simple fraction answers
- Make sure the correct_answer is actually correct"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 800,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            result = json.loads(content)

            is_valid, error = MathVerifier.verify(
                result.get("question", ""),
                result.get("correct_answer", ""),
            )
            if not is_valid:
                return None

            return result
        except Exception:
            return None

    @staticmethod
    async def generate_explanation(kp_name: str, kp_description: str, student_mistake: str = "") -> str | None:
        """Generate a detailed explanation for a knowledge point."""
        if not LLM_API_KEY:
            return None

        prompt = f"""Explain the following math topic for a middle school student: {kp_name}.
Topic description: {kp_description}
{f'Common student mistake to address: {student_mistake}' if student_mistake else ''}

Provide a clear explanation in Chinese that:
1. Explains the key concept in simple terms
2. Shows one example
3. Highlights common pitfalls

Return ONLY the explanation text, no JSON wrapper."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5,
                        "max_tokens": 500,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    @staticmethod
    def is_configured() -> bool:
        return bool(LLM_API_KEY and LLM_BASE_URL and LLM_MODEL)
