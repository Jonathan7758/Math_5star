from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

import json

from backend.config import PARENT_PIN, KNOWLEDGE_GRAPH_PATH
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.store import store

router = APIRouter()

_graph: KnowledgeGraph | None = None


def _get_graph() -> KnowledgeGraph:
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph(KNOWLEDGE_GRAPH_PATH)
        _graph.load()
    return _graph


def _verify_pin(x_parent_pin: str | None = Header(None)):
    if x_parent_pin != PARENT_PIN:
        raise HTTPException(status_code=403, detail="Invalid PIN")


class MasteryHeatmapItem(BaseModel):
    kp_id: str
    kp_name: str
    grade: str
    score: float
    total_attempts: int
    correct_attempts: int


class WeeklyStats(BaseModel):
    date: str
    minutes: float
    accuracy: float
    questions: int


class PathNodeOut(BaseModel):
    order: int
    kp_id: str
    kp_name: str
    reason: str


class DashboardResponse(BaseModel):
    success: bool = True
    student_id: int
    student_name: str
    level: int
    streak_days: int
    total_xp: int
    mastery_heatmap: list[MasteryHeatmapItem]
    weekly_stats: list[WeeklyStats]
    current_path: list[PathNodeOut] = []
    suggestions: list[str] = []


class GraphNode(BaseModel):
    kp_id: str
    kp_name: str
    grade: str
    score: float
    total_attempts: int

class GraphEdge(BaseModel):
    source: str
    target: str

class GraphResponse(BaseModel):
    success: bool = True
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class PathAdjustment(BaseModel):
    path_id: int | None = None
    adjustments: dict[str, int] = {}


@router.get("/api/parent/dashboard", response_model=DashboardResponse)
async def parent_dashboard(student_id: int, x_parent_pin: str = Header(None)):
    _verify_pin(x_parent_pin)
    g = _get_graph()
    student = store.get_or_create_student(student_id)
    mastery_data = store.get_mastery_heatmap(student_id)
    mastery_by_kp = {m["kp_id"]: m for m in mastery_data}

    heatmap = []
    for node_id in g.digraph.nodes:
        try:
            node = g.get_node(node_id)
        except KeyError:
            node = {"id": node_id, "name": node_id, "grade": "Y7"}
        m = mastery_by_kp.get(node_id, {"score": 0.0, "attempts": 0, "correct": 0})
        heatmap.append(MasteryHeatmapItem(
            kp_id=node_id,
            kp_name=node.get("name", node_id),
            grade=node.get("grade", "Y7"),
            score=round(m.get("score", 0.0), 2),
            total_attempts=m.get("attempts", 0),
            correct_attempts=m.get("correct", 0),
        ))

    stats_data = store.get_weekly_stats(student_id)
    stats = [
        WeeklyStats(date=s["date"], minutes=s["minutes"], accuracy=s["accuracy"], questions=s["questions"])
        for s in stats_data
    ]

    path_raw = store.get_learning_path(student_id)
    path_data = []
    for pn in path_raw:
        path_data.append(PathNodeOut(
            order=pn.get("order", 0),
            kp_id=pn.get("kp_id", ""),
            kp_name=pn.get("kp_name", pn.get("kp_id", "")),
            reason=pn.get("reason", ""),
        ))

    suggestions = []
    weak_items = [h for h in heatmap if h.score < 0.5 and h.total_attempts > 0]
    if weak_items:
        names = ", ".join([w.kp_name for w in weak_items[:5]])
        suggestions.append(f"建议优先攻克: {names}")
    if heatmap and all(h.score < 0.1 for h in heatmap):
        suggestions.append("建议先完成一次完整诊断，了解当前掌握情况")
    if not stats:
        suggestions.append("尚未有学习记录，鼓励孩子开始使用")

    return DashboardResponse(
        student_id=student_id,
        student_name=student.name or f"Student {student_id}",
        level=student.level or 1,
        streak_days=student.current_streak_days or 0,
        total_xp=student.total_xp or 0,
        mastery_heatmap=heatmap,
        weekly_stats=stats,
        current_path=path_data,
        suggestions=suggestions,
    )


@router.post("/api/parent/approve-path")
async def approve_path(student_id: int, req: PathAdjustment, x_parent_pin: str = Header(None)):
    _verify_pin(x_parent_pin)

    path = store.approve_path(student_id, req.adjustments)
    if path is None:
        raise HTTPException(status_code=404, detail="No learning path found")

    return {"success": True, "status": "approved", "path": path}


@router.get("/api/parent/graph", response_model=GraphResponse)
async def knowledge_graph_view(student_id: int, x_parent_pin: str = Header(None)):
    _verify_pin(x_parent_pin)
    g = _get_graph()
    mastery_data = store.get_mastery_heatmap(student_id)
    mastery_by_kp = {m["kp_id"]: m for m in mastery_data}

    nodes = []
    for node_id in g.digraph.nodes:
        try:
            node = g.get_node(node_id)
        except KeyError:
            node = {"id": node_id, "name": node_id, "grade": "Y7"}
        m = mastery_by_kp.get(node_id, {"score": 0.0, "attempts": 0})
        nodes.append(GraphNode(
            kp_id=node_id,
            kp_name=node.get("name", node_id),
            grade=node.get("grade", "Y7"),
            score=round(m.get("score", 0.0), 2),
            total_attempts=m.get("attempts", 0),
        ))

    edges = []
    for src, tgt in g.digraph.edges:
        edges.append(GraphEdge(source=src, target=tgt))

    return GraphResponse(nodes=nodes, edges=edges)


def update_mastery(student_id: int, kp_id: str, is_correct: bool):
    store.update_mastery(student_id, kp_id, is_correct)


def set_learning_path(student_id: int, path: list[dict]):
    store.set_learning_path(student_id, path)


def add_weekly_stat(student_id: int, date_str: str, minutes: float, accuracy: float, questions: int):
    store.add_weekly_stat(student_id, date_str, minutes, accuracy, questions)
