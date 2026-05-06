from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import DIAGNOSTIC_ERROR_THRESHOLD, DIAGNOSTIC_BFS_MAX_DEPTH, KNOWLEDGE_GRAPH_PATH
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.agents.diagnostic_agent import DiagnosticAgent

router = APIRouter()

_knowledge_graph: KnowledgeGraph | None = None
_diagnostic_agent: DiagnosticAgent | None = None


def get_diagnostic_agent() -> DiagnosticAgent:
    global _knowledge_graph, _diagnostic_agent
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
        _knowledge_graph.load()
    if _diagnostic_agent is None:
        _diagnostic_agent = DiagnosticAgent(
            _knowledge_graph,
            error_threshold=DIAGNOSTIC_ERROR_THRESHOLD,
            max_depth=DIAGNOSTIC_BFS_MAX_DEPTH,
        )
    return _diagnostic_agent


class DiagnoseRecord(BaseModel):
    kp_id: str
    is_correct: bool


class DiagnoseRequest(BaseModel):
    student_id: int
    records: list[DiagnoseRecord]


class RootCauseOut(BaseModel):
    kp_id: str
    kp_name: str
    priority: float
    error_count: int
    impacted_nodes: list[str]
    reason: str


class DiagnoseResponse(BaseModel):
    success: bool = True
    root_causes: list[RootCauseOut]
    total_records: int
    incorrect_count: int


@router.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest):
    if not req.records:
        raise HTTPException(status_code=400, detail="No records provided")

    agent = get_diagnostic_agent()
    records_dict = [{"kp_id": r.kp_id, "is_correct": r.is_correct} for r in req.records]
    results = agent.analyze(records_dict)

    root_causes = [
        RootCauseOut(
            kp_id=rc.kp_id,
            kp_name=rc.kp_name,
            priority=rc.priority,
            error_count=rc.error_count,
            impacted_nodes=rc.impacted_nodes,
            reason=rc.reason,
        )
        for rc in results
    ]

    incorrect_count = sum(1 for r in req.records if not r.is_correct)

    return DiagnoseResponse(
        root_causes=root_causes,
        total_records=len(req.records),
        incorrect_count=incorrect_count,
    )
