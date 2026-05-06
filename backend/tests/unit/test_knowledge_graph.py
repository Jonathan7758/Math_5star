import pytest
from pathlib import Path
from backend.engine.knowledge_graph import KnowledgeGraph

SAMPLE_GRAPH = {
    "nodes": [
        {"id": "A", "name": "Topic A", "grade": "Y7"},
        {"id": "B", "name": "Topic B", "grade": "Y8"},
        {"id": "C", "name": "Topic C", "grade": "Y9"},
    ],
    "edges": [
        {"from": "A", "to": "B"},
        {"from": "B", "to": "C"},
    ],
}


@pytest.fixture
def graph_file(tmp_path):
    import json
    path = tmp_path / "test_graph.json"
    path.write_text(json.dumps(SAMPLE_GRAPH), encoding="utf-8")
    return str(path)


@pytest.fixture
def empty_graph_file(tmp_path):
    import json
    path = tmp_path / "empty_graph.json"
    path.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")
    return str(path)


class TestKnowledgeGraph:
    def test_load_valid_graph(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        g = kg.load()
        assert g.number_of_nodes() == 3
        assert g.number_of_edges() == 2
        assert kg.is_loaded()

    def test_load_missing_file(self):
        kg = KnowledgeGraph("/nonexistent/path.json")
        with pytest.raises(FileNotFoundError):
            kg.load()

    def test_load_empty_graph(self, empty_graph_file):
        kg = KnowledgeGraph(empty_graph_file)
        g = kg.load()
        assert g.number_of_nodes() == 0

    def test_get_node(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        node = kg.get_node("A")
        assert node["id"] == "A"
        assert node["name"] == "Topic A"
        assert node["grade"] == "Y7"

    def test_get_node_not_found(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        with pytest.raises(KeyError):
            kg.get_node("Z")

    def test_get_prerequisites(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        prereqs = kg.get_prerequisites("B")
        assert prereqs == ["A"]

    def test_get_prerequisites_none(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        prereqs = kg.get_prerequisites("A")
        assert prereqs == []

    def test_get_dependents(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        dependents = kg.get_dependents("B")
        assert dependents == ["C"]

    def test_bfs_upstream(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        results = kg.bfs_upstream("C")
        depths = {n: d for n, d in results}
        assert depths["B"] == 1
        assert depths["A"] == 2

    def test_bfs_upstream_max_depth(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        results = kg.bfs_upstream("C", max_depth=1)
        depths = {n: d for n, d in results}
        assert "B" in depths
        assert "A" not in depths

    def test_bfs_upstream_unknown_node(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        results = kg.bfs_upstream("Z")
        assert results == []

    def test_topological_sort(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        order = kg.topological_sort(["A", "B", "C"])
        assert order.index("A") < order.index("B") < order.index("C")

    def test_topological_sort_cycle(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        kg.load()
        kg.digraph.add_edge("C", "A")
        with pytest.raises(ValueError, match="Cycle"):
            kg.topological_sort(["A", "B", "C"])

    def test_node_count(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        assert kg.node_count == 3

    def test_edge_count(self, graph_file):
        kg = KnowledgeGraph(graph_file)
        assert kg.edge_count == 2

    def test_isolated_node(self, tmp_path):
        import json
        data = {
            "nodes": [
                {"id": "X", "name": "Isolated"},
                {"id": "Y", "name": "Connected"},
            ],
            "edges": [],
        }
        path = tmp_path / "iso.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        kg = KnowledgeGraph(str(path))
        prereqs = kg.get_prerequisites("X")
        assert prereqs == []
        deps = kg.get_dependents("X")
        assert deps == []
