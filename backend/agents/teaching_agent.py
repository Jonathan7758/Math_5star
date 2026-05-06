from dataclasses import dataclass


@dataclass
class QuestionData:
    question_id: str
    knowledge_point_id: str
    level: int
    question: str
    options: list[str] | None
    question_type: str
    correct_answer: str
    hints: list[str]
    explanation: str


@dataclass
class TeachingResult:
    is_correct: bool
    xp_earned: int
    hint: str | None
    hint_level: int
    explanation: str | None
    correct_answer: str
    should_retry: bool


class TeachingAgent:
    MAX_HINTS = 3

    def evaluate_answer(
        self,
        question: QuestionData,
        student_answer: str,
        previous_attempts: int = 0,
        hint_level_used: int = 0,
    ) -> TeachingResult:
        from backend.engine.math_verifier import MathVerifier

        result = MathVerifier.verify(student_answer, question.correct_answer)

        if result["is_correct"]:
            return TeachingResult(
                is_correct=True,
                xp_earned=10,
                hint=None,
                hint_level=0,
                explanation=None,
                correct_answer=question.correct_answer,
                should_retry=False,
            )

        next_hint_level = hint_level_used + 1

        if next_hint_level <= len(question.hints):
            hint = question.hints[next_hint_level - 1]
            return TeachingResult(
                is_correct=False,
                xp_earned=0,
                hint=hint,
                hint_level=next_hint_level,
                explanation=None,
                correct_answer=question.correct_answer,
                should_retry=next_hint_level < self.MAX_HINTS,
            )

        return TeachingResult(
            is_correct=False,
            xp_earned=0,
            hint=None,
            hint_level=self.MAX_HINTS,
            explanation=question.explanation or f"The correct answer is {question.correct_answer}.",
            correct_answer=question.correct_answer,
            should_retry=False,
        )

    def should_continue(self, hint_level: int) -> bool:
        return hint_level < self.MAX_HINTS
