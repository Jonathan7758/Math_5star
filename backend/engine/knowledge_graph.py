import json
from pathlib import Path
from typing import Optional

import networkx as nx


class KnowledgeGraph:
    def __init__(self, graph_path: str):
        self.graph_path = Path(graph_path)
        self.digraph: nx.DiGraph = nx.DiGraph()
        self._loaded = False

    def load(self) -> nx.DiGraph:
        if not self.graph_path.exists():
            raise FileNotFoundError(f"Knowledge graph not found: {self.graph_path}")
        with open(self.graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        self.digraph = nx.DiGraph()
        for node in nodes:
            self.digraph.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
        for edge in edges:
            self.digraph.add_edge(edge["from"], edge["to"])
        self._loaded = True
        return self.digraph

    def get_node(self, node_id: str) -> dict:
        if not self._loaded:
            self.load()
        if node_id not in self.digraph:
            raise KeyError(f"Node not found: {node_id}")
        return {"id": node_id, **self.digraph.nodes[node_id]}

    def get_prerequisites(self, node_id: str) -> list[str]:
        if not self._loaded:
            self.load()
        if node_id not in self.digraph:
            return []
        return list(self.digraph.predecessors(node_id))

    def get_dependents(self, node_id: str) -> list[str]:
        if not self._loaded:
            self.load()
        if node_id not in self.digraph:
            return []
        return list(self.digraph.successors(node_id))

    def bfs_upstream(self, node_id: str, max_depth: int = 5) -> list[tuple[str, int]]:
        if not self._loaded:
            self.load()
        if node_id not in self.digraph:
            return []
        visited: dict[str, int] = {}
        queue = [(node_id, 0)]
        while queue:
            current, depth = queue.pop(0)
            if depth > max_depth:
                continue
            if current not in visited:
                visited[current] = depth
                for pred in self.digraph.predecessors(current):
                    queue.append((pred, depth + 1))
        return [(n, d) for n, d in visited.items() if n != node_id]

    def topological_sort(self, node_ids: list[str]) -> list[str]:
        if not self._loaded:
            self.load()
        subgraph = self.digraph.subgraph(node_ids)
        try:
            return list(nx.topological_sort(subgraph))
        except nx.NetworkXUnfeasible:
            raise ValueError("Cycle detected in dependency graph")

    @property
    def node_count(self) -> int:
        if not self._loaded:
            self.load()
        return self.digraph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        if not self._loaded:
            self.load()
        return self.digraph.number_of_edges()

    def is_loaded(self) -> bool:
        return self._loaded
