from dataclasses import dataclass, field
from backend.engine.knowledge_graph import KnowledgeGraph
from backend.agents.diagnostic_agent import RootCause


@dataclass
class PathNode:
    order: int
    kp_id: str
    kp_name: str
    reason: str
    prerequisites_met: list[str] = field(default_factory=list)


@dataclass
class LearningPath:
    path: list[PathNode]
    estimated_sessions: int
    summary: str


class PlanningAgent:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph

    def generate_path(self, root_causes: list[RootCause]) -> LearningPath:
        if not root_causes:
            return LearningPath(path=[], estimated_sessions=0, summary="No weak areas found.")

        target_ids = {rc.kp_id for rc in root_causes}
        all_node_ids = set(target_ids)
        for rc in root_causes:
            for impacted in rc.impacted_nodes:
                all_node_ids.add(impacted)

        ancestors = set()
        for nid in list(all_node_ids):
            upstream = self.graph.bfs_upstream(nid, max_depth=10)
            for ancestor_id, _ in upstream:
                ancestors.add(ancestor_id)
        all_node_ids |= ancestors

        all_node_ids_in_graph = {
            nid for nid in all_node_ids
            if nid in self.graph.digraph
        }

        if not all_node_ids_in_graph:
            return LearningPath(path=[], estimated_sessions=0, summary="No matching knowledge points in graph.")

        try:
            sorted_ids = self.graph.topological_sort(list(all_node_ids_in_graph))
        except ValueError:
            sorted_ids = self._fallback_sort(list(all_node_ids_in_graph))

        path = []
        for i, kp_id in enumerate(sorted_ids, 1):
            try:
                node = self.graph.get_node(kp_id)
                name = node.get("name", kp_id)
            except KeyError:
                name = kp_id

            prereqs = self.graph.get_prerequisites(kp_id)
            prereqs_in_path = [p for p in prereqs if p in all_node_ids_in_graph and p != kp_id]

            reason = self._build_reason(kp_id, name, prereqs_in_path, target_ids)

            path.append(PathNode(
                order=i,
                kp_id=kp_id,
                kp_name=name,
                reason=reason,
                prerequisites_met=prereqs_in_path,
            ))

        estimated_sessions = max(1, len(path) // 3)

        root_names = []
        for rc in root_causes:
            try:
                node = self.graph.get_node(rc.kp_id)
                root_names.append(node.get("name", rc.kp_id))
            except KeyError:
                root_names.append(rc.kp_id)

        summary = f"学习路径共 {len(path)} 个知识点，预计需要 {estimated_sessions} 次学习会话完成。"

        return LearningPath(
            path=path,
            estimated_sessions=estimated_sessions,
            summary=summary,
        )

    def _build_reason(self, kp_id: str, name: str, prereqs: list[str], targets: set[str]) -> str:
        parts = []
        if kp_id in targets:
            parts.append(f"这是你的薄弱环节")
        if prereqs:
            prereq_names = []
            for p in prereqs[:3]:
                try:
                    pn = self.graph.get_node(p)
                    prereq_names.append(pn.get("name", p))
                except KeyError:
                    prereq_names.append(p)
            parts.append(f"前置知识: {', '.join(prereq_names)}")
        if not parts:
            parts.append("基础知识点，无前置依赖")
        return "；".join(parts)

    def _fallback_sort(self, node_ids: list[str]) -> list[str]:
        result = []
        remaining = set(node_ids)
        while remaining:
            found = None
            for nid in list(remaining):
                prereqs = self.graph.get_prerequisites(nid)
                if all(p not in remaining or p == nid for p in prereqs):
                    found = nid
                    break
            if found is None:
                result.extend(sorted(remaining))
                break
            result.append(found)
            remaining.remove(found)
        return result
