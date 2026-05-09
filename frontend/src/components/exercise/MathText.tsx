import { useEffect, useRef, useState } from 'react'

interface MathTextProps {
  text: string
  className?: string
}

// Fallback: simple inline LaTeX detection and rendering
// Supports: \( ... \), \[ ... \], $...$, and $$...$$
function renderMathFallback(text: string): string {
  let result = text
  // Display math: $$...$$ or \[...\]
  result = result.replace(/\$\$([^$]+)\$\$|\\\[([^\]]+)\\\]/g, (_, m1, m2) => {
    const formula = (m1 || m2 || '').trim()
    return `<span class="math-block">${escapeHtml(formula)}</span>`
  })
  // Inline math: $...$ or \(...\)
  result = result.replace(/\$([^$]+)\$|\\\(([^)]+)\\\)/g, (_, m1, m2) => {
    const formula = (m1 || m2 || '').trim()
    return `<span class="math-inline">${escapeHtml(formula)}</span>`
  })
  return result
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// Also convert common math operators to nicer Unicode
function prettifyMath(text: string): string {
  return text
    .replace(/×/g, '×')
    .replace(/÷/g, '÷')
    .replace(/−/g, '−')
    .replace(/≤/g, '≤')
    .replace(/≥/g, '≥')
    .replace(/²/g, '²')
    .replace(/³/g, '³')
    .replace(/√/g, '√')
    .replace(/π/g, 'π')
    .replace(/θ/g, 'θ')
    .replace(/Δ/g, 'Δ')
    .replace(/∞/g, '∞')
    .replace(/∑/g, '∑')
    .replace(/∏/g, '∏')
    .replace(/∫/g, '∫')
}

declare global {
  interface Window {
    MathJax?: {
      typesetPromise?: (elements?: HTMLElement[]) => Promise<void>
      typeset?: (elements?: HTMLElement[]) => void
    }
  }
}

export function MathText({ text, className = '' }: MathTextProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const hasLatex = /[\$\\]/.test(text)
  const displayText = prettifyMath(text)

  useEffect(() => {
    if (!containerRef.current) return
    if (!hasLatex || displayText.includes('\\\\')) return

    // Use MathJax if available, otherwise keep raw HTML
    if (window.MathJax?.typesetPromise) {
      try {
        window.MathJax.typesetPromise([containerRef.current]).catch(() => {})
      } catch {
        // MathJax typeset failed, fallback rendered content is fine
      }
    }
  }, [displayText, hasLatex])

  if (!hasLatex || displayText.includes('\\\\')) {
    return (
      <div className={`text-white leading-relaxed font-mono tracking-wide ${className}`}>
        {displayText}
      </div>
    )
  }

  const html = renderMathFallback(displayText)

  return (
    <div
      ref={containerRef}
      className={`math-content text-white leading-relaxed ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
