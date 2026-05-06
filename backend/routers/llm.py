from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agents.llm_agent import LLMAgent
from backend.config import KNOWLEDGE_GRAPH_PATH
from backend.engine.knowledge_graph import KnowledgeGraph

router = APIRouter()


class GenerateQuestionRequest(BaseModel):
    kp_id: str
    level: int = 1


@router.post("/api/llm/generate-question")
async def generate_question(req: GenerateQuestionRequest):
    if not LLMAgent.is_configured():
        raise HTTPException(status_code=503, detail="LLM API key not configured")

    kg = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
    kg.load()
    try:
        node = kg.get_node(req.kp_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Knowledge point {req.kp_id} not found")

    question = await LLMAgent.generate_question(
        kp_name=node.get("name", req.kp_id),
        kp_description=node.get("description", ""),
        grade=node.get("grade", "Y7"),
        level=req.level,
    )

    if question is None:
        raise HTTPException(status_code=500, detail="Failed to generate valid question (SymPy verification failed)")

    return {"success": True, "question": question}


@router.post("/api/llm/generate-explanation")
async def generate_explanation(req: GenerateQuestionRequest):
    if not LLMAgent.is_configured():
        raise HTTPException(status_code=503, detail="LLM API key not configured")

    kg = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
    kg.load()
    try:
        node = kg.get_node(req.kp_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Knowledge point {req.kp_id} not found")

    explanation = await LLMAgent.generate_explanation(
        kp_name=node.get("name", req.kp_id),
        kp_description=node.get("description", ""),
    )

    if explanation is None:
        raise HTTPException(status_code=500, detail="Failed to generate explanation")

    return {"success": True, "explanation": explanation}
