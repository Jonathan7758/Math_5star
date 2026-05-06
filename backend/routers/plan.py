from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import KNOWLEDGE_GRAPH_PATH
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.agents.planning_agent import PlanningAgent
from backend.routers.parent import set_learning_path

router = APIRouter()

_graph: KnowledgeGraph | None = None
_planner: PlanningAgent | None = None


def get_planner() -> PlanningAgent:
    global _graph, _planner
    if _graph is None:
        _graph = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
        _graph.load()
    if _planner is None:
        _planner = PlanningAgent(_graph)
    return _planner


class PlanRootCause(BaseModel):
    kp_id: str
    kp_name: str
    priority: float
    impacted_nodes: list[str] = []


class PlanRequest(BaseModel):
    student_id: int
    root_causes: list[PlanRootCause]


class PathNodeOut(BaseModel):
    order: int
    kp_id: str
    kp_name: str
    reason: str


class PlanResponse(BaseModel):
    success: bool = True
    path: list[PathNodeOut]
    estimated_sessions: int
    summary: str


@router.post("/api/plan", response_model=PlanResponse)
async def create_plan(req: PlanRequest):
    if not req.root_causes:
        raise HTTPException(status_code=400, detail="No root causes provided")

    from backend.agents.diagnostic_agent import RootCause
    root_causes = [
        RootCause(
            kp_id=rc.kp_id,
            kp_name=rc.kp_name,
            priority=rc.priority,
            error_count=0,
            impacted_nodes=rc.impacted_nodes,
            reason="",
        )
        for rc in req.root_causes
    ]

    planner = get_planner()
    result = planner.generate_path(root_causes)

    path_out = [
        PathNodeOut(
            order=pn.order,
            kp_id=pn.kp_id,
            kp_name=pn.kp_name,
            reason=pn.reason,
        )
        for pn in result.path
    ]

    path_dicts = [{"order": pn.order, "kp_id": pn.kp_id, "kp_name": pn.kp_name, "reason": pn.reason} for pn in result.path]
    set_learning_path(req.student_id, path_dicts)

    return PlanResponse(
        path=path_out,
        estimated_sessions=result.estimated_sessions,
        summary=result.summary,
    )
