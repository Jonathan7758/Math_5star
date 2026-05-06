import pytest
from backend.agents.teaching_agent import TeachingAgent, QuestionData


@pytest.fixture
def teaching_agent():
    return TeachingAgent()


@pytest.fixture
def sample_question():
    return QuestionData(
        question_id="Q1",
        knowledge_point_id="K01",
        level=1,
        question="What is 2 + 2?",
        options=["3", "4", "5"],
        question_type="multiple_choice",
        correct_answer="4",
        hints=["Count on your fingers: 2 then 3, 4", "Add the two numbers together"],
        explanation="2 + 2 = 4",
    )


@pytest.fixture
def fraction_question():
    return QuestionData(
        question_id="Q2",
        knowledge_point_id="K02",
        level=2,
        question="Simplify 12/16",
        options=None,
        question_type="numeric",
        correct_answer="3/4",
        hints=["Find the GCD of 12 and 16", "Divide both by 4"],
        explanation="12/16 = 3/4",
    )


class TestTeachingAgent:
    def test_verify_correct_answer(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "4")
        assert result.is_correct is True
        assert result.xp_earned == 10
        assert result.hint is None
        assert result.should_retry is False

    def test_verify_wrong_answer(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "3")
        assert result.is_correct is False
        assert result.xp_earned == 0
        assert result.hint is not None

    def test_verify_equivalent_form(self, teaching_agent, fraction_question):
        result = teaching_agent.evaluate_answer(fraction_question, "0.75")
        assert result.is_correct is True

    def test_hint_level_1(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "3", hint_level_used=0)
        assert result.hint_level == 1
        assert result.hint == "Count on your fingers: 2 then 3, 4"
        assert result.should_retry is True

    def test_hint_level_2(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "3", hint_level_used=1)
        assert result.hint_level == 2
        assert "Add" in result.hint
        assert result.should_retry is True

    def test_hint_level_3(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "3", hint_level_used=2)
        assert result.hint_level == 3
        assert result.explanation is not None
        assert result.should_retry is False

    def test_no_more_hints_after_max(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "3", hint_level_used=3)
        assert result.hint_level == 3
        assert result.should_retry is False

    def test_should_continue_below_max(self, teaching_agent):
        assert teaching_agent.should_continue(0) is True
        assert teaching_agent.should_continue(1) is True
        assert teaching_agent.should_continue(2) is True

    def test_should_not_continue_at_max(self, teaching_agent):
        assert teaching_agent.should_continue(3) is False

    def test_question_with_no_hints(self, teaching_agent):
        q = QuestionData(
            question_id="Q3", knowledge_point_id="K03", level=1,
            question="x?", options=None, question_type="numeric",
            correct_answer="42", hints=[], explanation="The answer is 42",
        )
        result = teaching_agent.evaluate_answer(q, "0")
        assert result.hint is None
        assert result.explanation is not None

    def test_invalid_answer_format(self, teaching_agent, sample_question):
        result = teaching_agent.evaluate_answer(sample_question, "!!!")
        assert result.is_correct is False
