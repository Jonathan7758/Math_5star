import json
import random
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import QUIZ_BANK_PATH, KNOWLEDGE_GRAPH_PATH
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.agents.teaching_agent import TeachingAgent, QuestionData
from backend.agents.storyteller_agent import storyteller
from backend.store import store

router = APIRouter()

_quiz_data: dict | None = None
_graph: KnowledgeGraph | None = None


def _load_quiz() -> dict:
    global _quiz_data
    if _quiz_data is None:
        path = Path(QUIZ_BANK_PATH)
        if not path.exists():
            return {"questions": []}
        _quiz_data = json.loads(path.read_text(encoding="utf-8"))
    return _quiz_data


def _get_graph() -> KnowledgeGraph:
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
        _graph.load()
    return _graph


class NextQuestionResponse(BaseModel):
    success: bool = True
    question_id: str
    knowledge_point_id: str
    level: int
    question: str
    options: list[str] | None = None
    question_type: str = "numeric"
    kp_name: str = ""
    story_question: str | None = None
    story_icon: str | None = None


class SubmitAnswerRequest(BaseModel):
    student_id: int
    question_id: str
    answer: str
    time_spent: float = 0
    hint_level_used: int = 0


class SubmitAnswerResponse(BaseModel):
    success: bool = True
    is_correct: bool
    correct_answer: str
    xp_earned: int = 0
    hint: str | None = None
    hint_level: int = 0
    should_retry: bool = False
    explanation: str | None = None


@router.get("/api/exercise/next", response_model=NextQuestionResponse)
async def next_question(student_id: int | None = None, kp_id: str | None = None):
    quiz = _load_quiz()
    questions: list[dict] = quiz.get("questions", [])

    if not questions:
        raise HTTPException(status_code=404, detail="No questions available")

    if kp_id:
        filtered = [q for q in questions if q["knowledge_point_id"] == kp_id]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No questions for {kp_id}")
        q = random.choice(filtered)
    else:
        q = random.choice(questions)

    kp_name = ""
    try:
        node = _get_graph().get_node(q["knowledge_point_id"])
        kp_name = node.get("name", "")
    except KeyError:
        pass

    return NextQuestionResponse(
        question_id=q["id"],
        knowledge_point_id=q["knowledge_point_id"],
        level=q.get("level", 1),
        question=q["question"],
        options=q.get("options"),
        question_type=q.get("type", "numeric"),
        kp_name=kp_name,
        story_question=None,  # Frontend calls /api/exercise/story for this
        story_icon=None,
    )


class StoryRequest(BaseModel):
    question_id: str
    question_text: str
    theme: str | None = None


@router.post("/api/exercise/story")
async def get_story(req: StoryRequest):
    """Get a storytelling version of a question."""
    result = await storyteller.get_story(req.question_id, req.question_text, req.theme)
    return {
        "success": True,
        "story_question": result["story_question"],
        "theme": result["theme"],
        "theme_name": result["theme_name"],
        "theme_icon": result["theme_icon"],
        "generated": result["generated"],
    }


@router.get("/api/exercise/themes")
async def get_themes():
    """Get available storytelling themes."""
    return {"success": True, "themes": storyteller.get_themes()}


@router.post("/api/exercise/submit", response_model=SubmitAnswerResponse)
async def submit_answer(req: SubmitAnswerRequest):
    quiz = _load_quiz()
    questions: list[dict] = quiz.get("questions", [])

    q = next((item for item in questions if item["id"] == req.question_id), None)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    question_data = QuestionData(
        question_id=q["id"],
        knowledge_point_id=q["knowledge_point_id"],
        level=q.get("level", 1),
        question=q["question"],
        options=q.get("options"),
        question_type=q.get("type", "numeric"),
        correct_answer=q["correct_answer"],
        hints=q.get("hints", []),
        explanation=q.get("explanation", ""),
    )

    agent = TeachingAgent()
    result = agent.evaluate_answer(
        question_data,
        req.answer,
        hint_level_used=req.hint_level_used,
    )

    store.record_answer(
        req.student_id,
        q["id"],
        q["knowledge_point_id"],
        result.is_correct,
        req.time_spent,
        result.hint_level,
    )

    return SubmitAnswerResponse(
        is_correct=result.is_correct,
        correct_answer=str(result.correct_answer),
        xp_earned=result.xp_earned,
        hint=result.hint,
        hint_level=result.hint_level,
        should_retry=result.should_retry,
        explanation=result.explanation,
    )
