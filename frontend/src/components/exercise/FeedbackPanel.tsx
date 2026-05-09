interface FeedbackPanelProps {
  isCorrect: boolean | null
  hint?: string | null
  explanation?: string | null
  hintLevel?: number
  xpEarned?: number
  combo?: number
  successText?: string
}

export function FeedbackPanel({
  isCorrect,
  hint,
  explanation,
  hintLevel,
  xpEarned,
  combo,
  successText,
}: FeedbackPanelProps) {
  return (
    <>
      {isCorrect && xpEarned !== undefined && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 text-green-400 text-sm">
          正确！+{xpEarned} XP {combo && combo >= 3 ? `· ${combo}连击` : ''}
        </div>
      )}
      {isCorrect && xpEarned === undefined && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 text-green-400 text-sm" role="status">
          {successText || '正确！'}
        </div>
      )}

      {hint && !isCorrect && (
        <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-3 text-orange-400 text-sm" role="status">
          {hintLevel !== undefined && hintLevel <= 1
            ? `💡 提示: ${hint}`
            : hint}
        </div>
      )}

      {isCorrect === false && explanation && (
        <div className="bg-slate-700/50 rounded-xl p-3 text-slate-300 text-sm" role="status">
          {explanation}
        </div>
      )}
    </>
  )
}
