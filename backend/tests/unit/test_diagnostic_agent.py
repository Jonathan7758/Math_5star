import json
import pytest
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.agents.diagnostic_agent import DiagnosticAgent, RootCause


SAMPLE_GRAPH = {
    "nodes": [
        {"id": "A", "name": "Addition"},
        {"id": "B", "name": "Multiplication"},
        {"id": "C", "name": "Fractions"},
        {"id": "D", "name": "Algebra"},
        {"id": "E", "name": "Geometry"},
    ],
    "edges": [
        {"from": "A", "to": "B"},
        {"from": "A", "to": "C"},
        {"from": "B", "to": "D"},
        {"from": "C", "to": "D"},
        {"from": "C", "to": "E"},
    ],
}


@pytest.fixture
def diagnostic_agent(tmp_path):
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(SAMPLE_GRAPH), encoding="utf-8")
    kg = KnowledgeGraph(str(path))
    kg.load()
    return DiagnosticAgent(kg)


class TestDiagnosticAgent:
    def test_empty_records(self, diagnostic_agent):
        result = diagnostic_agent.analyze([])
        assert result == []

    def test_all_correct_records(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": True},
            {"kp_id": "E", "is_correct": True},
        ]
        result = diagnostic_agent.analyze(records)
        assert result == []

    def test_single_error_trace_to_root(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        root_ids = {rc.kp_id for rc in result}
        assert len(root_ids) >= 2
        assert "A" in root_ids
        assert "B" in root_ids

    def test_deep_dependency_chain(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        priorities = {rc.kp_id: rc.priority for rc in result}
        assert "B" in priorities
        assert "C" in priorities
        assert priorities["A"] > 0.7
        assert abs(priorities["B"] - priorities["C"]) < 0.15

    def test_multiple_errors_aggregation(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
            {"kp_id": "D", "is_correct": False},
            {"kp_id": "E", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        ids = {rc.kp_id for rc in result}
        assert "C" in ids

    def test_priority_sorting(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
            {"kp_id": "E", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        for i in range(len(result) - 1):
            assert result[i].priority >= result[i + 1].priority

    def test_root_cause_has_reason(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        for rc in result:
            assert rc.reason != ""
            assert rc.kp_name != ""

    def test_root_cause_has_error_count(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
            {"kp_id": "D", "is_correct": False},
            {"kp_id": "B", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        for rc in result:
            assert rc.error_count >= 1

    def test_unknown_kp_id_graceful(self, diagnostic_agent):
        records = [
            {"kp_id": "Z", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        assert isinstance(result, list)

    def test_partial_correct_in_branch(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": True},
            {"kp_id": "E", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        root_ids = {rc.kp_id for rc in result}
        assert "C" in root_ids

    def test_root_cause_output_type(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        for rc in result:
            assert isinstance(rc, RootCause)
            assert isinstance(rc.kp_id, str)
            assert isinstance(rc.priority, float)

    def test_max_depth_respected(self, diagnostic_agent):
        diagnostic_agent.max_depth = 1
        records = [
            {"kp_id": "D", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        root_ids = {rc.kp_id for rc in result}
        assert "A" not in root_ids

    def test_impacted_nodes_included(self, diagnostic_agent):
        records = [
            {"kp_id": "D", "is_correct": False},
        ]
        result = diagnostic_agent.analyze(records)
        for rc in result:
            if rc.kp_id == "A":
                assert len(rc.impacted_nodes) >= 1
