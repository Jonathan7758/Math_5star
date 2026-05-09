import { useEffect, useRef, useState } from 'react'
import { masteryScoreHex } from '../../utils/mastery'
import { groupBy } from '../../utils/array'
import { EmptyState } from '../common/EmptyState'

interface GraphNode {
  kp_id: string
  kp_name: string
  grade: string
  score: number
  total_attempts: number
}

interface GraphEdge {
  source: string
  target: string
}

interface KnowledgeGraphProps {
  data: { nodes: GraphNode[]; edges: GraphEdge[] } | null
  onNodeClick: (node: GraphNode) => void
}

interface LayoutNode {
  x: number
  y: number
  node: GraphNode
}

export function KnowledgeGraph({ data, onNodeClick }: KnowledgeGraphProps) {
  const [tooltip, setTooltip] = useState<{ x: number; y: number; node: GraphNode } | null>(null)

  if (!data || data.nodes.length === 0) {
    return <EmptyState icon="🧭" message="暂无知识图谱数据" />
  }

  const gradeOrder: Record<string, number> = { Y7: 0, Y8: 1, Y9: 2 }

  const grouped = groupBy(data.nodes, (n) => n.grade)
  const grades = Object.keys(grouped).sort((a, b) => (gradeOrder[a] ?? 0) - (gradeOrder[b] ?? 0))

  const layoutMap = new Map<string, LayoutNode>()
  const GRADE_LABEL_HEIGHT = 28
  const NODE_HEIGHT = 48
  const TOP_MARGIN = 20
  const ROW_GAP = 18
  const COL_GAP = 12
  const PADDING = 40

  const viewWidth = 680
  let currentY = TOP_MARGIN + GRADE_LABEL_HEIGHT

  for (const grade of grades) {
    const nodes = grouped[grade]
    const rowCount = Math.ceil(nodes.length / 4)
    for (let row = 0; row < rowCount; row++) {
      const rowNodes = nodes.slice(row * 4, (row + 1) * 4)
      const cols = rowNodes.length
      const totalRowWidth = cols * 140 + (cols - 1) * COL_GAP
      const startX = (viewWidth - totalRowWidth) / 2
      for (let i = 0; i < cols; i++) {
        layoutMap.set(rowNodes[i].kp_id, {
          x: startX + i * (140 + COL_GAP) + 70,
          y: currentY + NODE_HEIGHT / 2,
          node: rowNodes[i],
        })
      }
      currentY += NODE_HEIGHT + ROW_GAP
    }
  }

  const viewHeight = Math.max(currentY + PADDING, 300)

  const nodeIdSet = new Set(data.nodes.map((n) => n.kp_id))
  const validEdges = data.edges.filter(
    (e) => nodeIdSet.has(e.source) && nodeIdSet.has(e.target)
  )

  const gradeLabels = grades.map((grade) => {
    const firstNode = grouped[grade][0]
    const firstLayout = layoutMap.get(firstNode.kp_id)
    if (!firstLayout) return null
    const labelY = firstLayout.y - NODE_HEIGHT / 2 - 4
    return { grade, x: PADDING + 8, y: labelY }
  }).filter(Boolean) as { grade: string; x: number; y: number }[]

  return (
    <div className="overflow-x-auto">
      <svg
        viewBox={`0 0 ${viewWidth} ${viewHeight}`}
        className="w-full"
        style={{ maxWidth: viewWidth, minHeight: viewHeight }}
      >
        <defs>
          <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#64748b" />
          </marker>
        </defs>

        {gradeLabels.map((gl) => (
          <g key={gl.grade}>
            <rect x={gl.x - 4} y={gl.y - 14} width={48} height={20} rx={4} fill="#1e293b" stroke="#475569" strokeWidth={0.5} />
            <text x={gl.x + 20} y={gl.y} textAnchor="middle" fill="#94a3b8" fontSize={10} fontWeight="bold" dominantBaseline="middle">
              {gl.grade}
            </text>
          </g>
        ))}

        {validEdges.map((edge, i) => {
          const s = layoutMap.get(edge.source)
          const t = layoutMap.get(edge.target)
          if (!s || !t) return null
          const midY = (s.y + t.y) / 2
          const dx = t.x - s.x
          const dy = t.y - s.y
          const offset = Math.abs(dx) * 0.3 + Math.min(Math.abs(dy) * 0.1, 12)
          return (
            <path
              key={i}
              d={`M ${s.x} ${s.y} Q ${s.x + offset} ${midY}, ${t.x} ${t.y}`}
              fill="none"
              stroke="#475569"
              strokeWidth={1.2}
              markerEnd="url(#arrowhead)"
              opacity={0.6}
            />
          )
        })}

        {Array.from(layoutMap.values()).map((ln) => {
          const color = masteryScoreHex(ln.node.score)
          return (
            <g
              key={ln.node.kp_id}
              className="cursor-pointer transition-transform hover:scale-105"
              role="button"
              tabIndex={0}
              aria-label={`${ln.node.kp_name}: ${Math.round(ln.node.score * 100)}% mastery`}
              onClick={() => onNodeClick(ln.node)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onNodeClick(ln.node) } }}
              onMouseEnter={(e) => {
                const rect = (e.currentTarget as SVGGElement).closest('svg')?.getBoundingClientRect()
                if (rect) {
                  const svgRect = (e.currentTarget as SVGGElement).closest('svg')!.getBoundingClientRect()
                  setTooltip({ x: ln.x + 80, y: ln.y - 50, node: ln.node })
                }
              }}
              onMouseLeave={() => setTooltip(null)}
            >
              <rect
                x={ln.x - 60}
                y={ln.y - 20}
                width={120}
                height={40}
                rx={8}
                fill={color}
                fillOpacity={0.25}
                stroke={color}
                strokeWidth={1.5}
              />
              <text
                x={ln.x}
                y={ln.y - 2}
                textAnchor="middle"
                fill="#e2e8f0"
                fontSize={10}
                fontWeight="bold"
              >
                {ln.node.kp_name.length > 14 ? ln.node.kp_name.slice(0, 13) + '…' : ln.node.kp_name}
              </text>
              <text
                x={ln.x}
                y={ln.y + 12}
                textAnchor="middle"
                fill="#94a3b8"
                fontSize={9}
              >
                {ln.node.total_attempts > 0 ? `${Math.round(ln.node.score * 100)}%` : '未练习'}
              </text>
            </g>
          )
        })}

        {tooltip && (
          <g pointerEvents="none">
            <rect
              x={Math.min(tooltip.x - 50, viewWidth - 140)}
              y={tooltip.y - 20}
              width={100}
              height={40}
              rx={6}
              fill="#1e293b"
              stroke="#475569"
              strokeWidth={1}
              opacity={0.95}
            />
            <text
              x={Math.min(tooltip.x, viewWidth - 40)}
              y={tooltip.y}
              textAnchor="middle"
              fill="#e2e8f0"
              fontSize={10}
              fontWeight="bold"
            >
              {tooltip.node.kp_name}
            </text>
            <text
              x={Math.min(tooltip.x, viewWidth - 40)}
              y={tooltip.y + 14}
              textAnchor="middle"
              fill="#94a3b8"
              fontSize={9}
            >
              {tooltip.node.total_attempts > 0 ? `${Math.round(tooltip.node.score * 100)}%` : '未练习'}
            </text>
          </g>
        )}
      </svg>
    </div>
  )
}
