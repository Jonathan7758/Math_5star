interface AnswerInputProps {
  value: string
  onChange: (val: string) => void
  disabled: boolean
  placeholder?: string
  ariaLabel?: string
  isCorrect?: boolean | null
}

export function AnswerInput({
  value,
  onChange,
  disabled,
  placeholder = '输入答案...',
  ariaLabel = '输入答案',
  isCorrect,
}: AnswerInputProps) {
  return (
    <input
      type="text"
      inputMode="decimal"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder={placeholder}
      aria-label={ariaLabel}
      className={`w-full p-3 rounded-xl border bg-slate-900 min-h-[48px] text-white text-lg text-center transition-colors ${
        isCorrect === true ? 'border-green-500 bg-green-500/10' :
        isCorrect === false ? 'border-orange-500 bg-orange-500/10' :
        'border-slate-700 focus:border-primary-500'
      }`}
    />
  )
}
