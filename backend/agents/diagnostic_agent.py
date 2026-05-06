from dataclasses import dataclass, field
from typing import Optional

from backend.engine.knowledge_graph import KnowledgeGraph


@dataclass
class RootCause:
    kp_id: str
    kp_name: str
    priority: float
    error_count: int
    impacted_nodes: list[str] = field(default_factory=list)
    reason: str = ""
    depth_from_error: int = 0


class DiagnosticAgent:
    def __init__(self, knowledge_graph: KnowledgeGraph, error_threshold: float = 0.3, max_depth: int = 5):
        self.graph = knowledge_graph
        self.error_threshold = error_threshold
        self.max_depth = max_depth

    def analyze(self, records: list[dict]) -> list[RootCause]:
        if not records:
            return []

        incorrect_kps = [r["kp_id"] for r in records if not r.get("is_correct", True)]

        if not incorrect_kps:
            return []

        frequency: dict[str, int] = {}
        impact_map: dict[str, list[str]] = {}

        for kp_id in incorrect_kps:
            upstream = self.graph.bfs_upstream(kp_id, max_depth=self.max_depth)
            if not upstream:
                if kp_id not in frequency:
                    frequency[kp_id] = 0
                frequency[kp_id] += 1
                impact_map.setdefault(kp_id, []).append(kp_id)
                continue

            for ancestor_id, depth in upstream:
                if ancestor_id not in frequency:
                    frequency[ancestor_id] = 0
                frequency[ancestor_id] += 1
                impact_map.setdefault(ancestor_id, []).append(kp_id)

        if not frequency:
            return []

        max_freq = max(frequency.values())
        normalized: dict[str, float] = {}
        for kp_id, count in frequency.items():
            dependents = self._get_downstream_impact(kp_id)
            norm_freq = count / max_freq
            norm_dep = min(dependents / 10.0, 1.0)
            normalized[kp_id] = 0.6 * norm_freq + 0.4 * norm_dep

        error_counts = frequency.copy()
        for kp_id in incorrect_kps:
            if kp_id not in error_counts:
                error_counts[kp_id] = 0

        sorted_candidates = sorted(frequency.items(), key=lambda x: normalized[x[0]], reverse=True)

        root_causes = []
        for kp_id, count in sorted_candidates:
            priority = normalized[kp_id]
            try:
                node = self.graph.get_node(kp_id)
                name = node.get("name", kp_id)
            except KeyError:
                name = kp_id

            reason = self._build_reason(kp_id, count, impact_map.get(kp_id, []))
            root_causes.append(RootCause(
                kp_id=kp_id,
                kp_name=name,
                priority=round(priority, 3),
                error_count=count,
                impacted_nodes=impact_map.get(kp_id, []),
                reason=reason,
            ))

        root_causes.sort(key=lambda rc: rc.priority, reverse=True)
        return root_causes

    def _get_downstream_impact(self, kp_id: str) -> int:
        try:
            deps = self.graph.get_dependents(kp_id)
            count = len(deps)
            visited = set(deps)
            queue = list(deps)
            while queue:
                current = queue.pop(0)
                for child in self.graph.get_dependents(current):
                    if child not in visited:
                        visited.add(child)
                        count += 1
                        queue.append(child)
            return count
        except KeyError:
            return 0

    def _build_reason(self, kp_id: str, error_count: int, impacted_nodes: list[str]) -> str:
        try:
            node = self.graph.get_node(kp_id)
            name = node.get("name", kp_id)
        except KeyError:
            name = kp_id

        parts = [f"{name}({kp_id}) 出现了 {error_count} 次关联错误"]
        if impacted_nodes:
            if kp_id in impacted_nodes:
                impacted = [n for n in impacted_nodes if n != kp_id]
                if impacted:
                    parts.append(f"这影响了 {len(impacted)} 个下游知识点的学习")
            else:
                parts.append(f"这影响了 {len(impacted_nodes)} 个下游知识点的学习: {', '.join(impacted_nodes[:3])}")
        return "；".join(parts)
