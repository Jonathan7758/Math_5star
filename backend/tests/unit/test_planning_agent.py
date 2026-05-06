import json
import pytest
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.agents.planning_agent import PlanningAgent, LearningPath
from backend.agents.diagnostic_agent import RootCause


SAMPLE_GRAPH = {
    "nodes": [
        {"id": "A", "name": "Addition"},
        {"id": "B", "name": "Multiplication"},
        {"id": "C", "name": "Fractions"},
        {"id": "D", "name": "Algebra"},
    ],
    "edges": [
        {"from": "A", "to": "B"},
        {"from": "A", "to": "C"},
        {"from": "B", "to": "D"},
        {"from": "C", "to": "D"},
    ],
}


@pytest.fixture
def planning_agent(tmp_path):
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(SAMPLE_GRAPH), encoding="utf-8")
    kg = KnowledgeGraph(str(path))
    kg.load()
    return PlanningAgent(kg)


class TestPlanningAgent:
    def test_generate_path_single_root(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        assert len(result.path) >= 2
        assert result.estimated_sessions >= 1
        assert result.summary != ""

    def test_generate_path_multiple_roots(self, planning_agent):
        root_causes = [
            RootCause(kp_id="B", kp_name="Multiplication", priority=0.7, error_count=2, impacted_nodes=["B", "D"], reason=""),
            RootCause(kp_id="C", kp_name="Fractions", priority=0.6, error_count=2, impacted_nodes=["C"], reason=""),
        ]
        result = planning_agent.generate_path(root_causes)
        assert len(result.path) >= 3

    def test_prerequisite_order(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        ids = [pn.kp_id for pn in result.path]
        assert ids.index("A") < ids.index("B")
        assert ids.index("A") < ids.index("C")
        assert ids.index("B") < ids.index("D")

    def test_path_includes_reason(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        for pn in result.path:
            assert pn.reason != ""
            assert pn.kp_name != ""
            assert isinstance(pn.order, int)

    def test_empty_root_causes(self, planning_agent):
        result = planning_agent.generate_path([])
        assert result.path == []
        assert result.estimated_sessions == 0

    def test_all_nodes_covered(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        ids = {pn.kp_id for pn in result.path}
        assert "A" in ids
        assert "B" in ids
        assert "C" in ids
        assert "D" in ids

    def test_independent_branches_parallel(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        ids = [pn.kp_id for pn in result.path]
        b_pos = ids.index("B")
        c_pos = ids.index("C")
        assert b_pos < ids.index("D")
        assert c_pos < ids.index("D")

    def test_estimated_session_count(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        assert result.estimated_sessions >= 1
        assert result.estimated_sessions <= len(result.path)

    def test_no_prerequisite_roots_first(self, planning_agent):
        root_causes = [RootCause(kp_id="D", kp_name="Algebra", priority=0.8, error_count=3, impacted_nodes=["D"], reason="")]
        result = planning_agent.generate_path(root_causes)
        if result.path:
            assert result.path[0].kp_id == "A"
