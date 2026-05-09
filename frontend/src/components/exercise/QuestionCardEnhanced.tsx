import { useState, useEffect } from 'react'
import { MathText } from './MathText'
import { MultipleChoiceOptions } from './MultipleChoiceOptions'
import { AnswerInput } from './AnswerInput'
import { FeedbackPanel } from './FeedbackPanel'

interface QuestionData {
  question_id: string
  knowledge_point_id: string
  level: number
  question: string
  options: string[] | null
  question_type: string
  kp_name: string
}

interface EncMsg {
  text: string
  emoji: string
}

const ENCOURAGEMENTS: EncMsg[] = [
  { text: '仔细读题，你一定可以的！', emoji: '💪' },
  { text: '先理解题目的意思再作答哦~', emoji: '🤔' },
  { text: '遇到计算题要一步一步来！', emoji: '📝' },
  { text: '别着急，慢慢想，你做得到~', emoji: '🌟' },
  { text: '检查一下你的答案再提交！', emoji: '🔍' },
  { text: '数学就是要多动脑筋！', emoji: '🧠' },
  { text: '读题时注意看数字和符号~', emoji: '👀' },
]

const CORRECT_MSGS: EncMsg[] = [
  { text: '太棒了！答对了！', emoji: '🎉' },
  { text: '完全正确！继续加油！', emoji: '✨' },
  { text: '好厉害，就是这样做！', emoji: '👏' },
  { text: '完美！你越来越强了！', emoji: '💯' },
]

const WRONG_MSGS: EncMsg[] = [
  { text: '别灰心，看看提示再试试！', emoji: '💡' },
  { text: '差一点点，再想想看~', emoji: '🤗' },
  { text: '没关系，错误是学习的一部分！', emoji: '📚' },
  { text: '仔细看解析，下次就会了！', emoji: '🔎' },
]

interface ThemeGradient {
  card: string
  border: string
  accent: string
}

const THEME_STYLES: Record<string, ThemeGradient> = {
  fruit_shop:  { card: 'from-rose-500/10 to-orange-600/10', border: 'border-rose-500/30', accent: 'text-rose-400' },
  animals:     { card: 'from-emerald-500/10 to-green-700/10', border: 'border-emerald-500/30', accent: 'text-emerald-400' },
  space:       { card: 'from-indigo-500/15 to-purple-700/10', border: 'border-indigo-500/30', accent: 'text-indigo-400' },
  game_world:  { card: 'from-cyan-500/10 to-blue-600/10', border: 'border-cyan-500/30', accent: 'text-cyan-400' },
  baking:      { card: 'from-amber-500/10 to-yellow-700/10', border: 'border-amber-500/30', accent: 'text-amber-400' },
  sports:      { card: 'from-red-500/10 to-orange-600/10', border: 'border-red-500/30', accent: 'text-red-400' },
  ocean:       { card: 'from-sky-500/10 to-teal-700/10', border: 'border-sky-500/30', accent: 'text-sky-400' },
  carnival:    { card: 'from-pink-500/10 to-fuchsia-600/10', border: 'border-pink-500/30', accent: 'text-pink-400' },
}

function getThemeStyle(themeKey: string | undefined | null): ThemeGradient {
  return (themeKey && THEME_STYLES[themeKey]) || { card: 'from-blue-500/20 to-blue-600/10', border: 'border-blue-500/30', accent: 'text-blue-400' }
}

interface QuestionCardEnhancedProps {
  question: QuestionData
  selectedAnswer: string | null
  onSelect: (answer: string) => void
  feedback: any
  hintLevel: number
  combo?: number
  questionIndex: number
  totalQuestions?: number
  mode: 'quiz' | 'diagnose'
  lowHearts?: boolean
  xpFlyText?: string | null
  xpFlyKey?: number
  storyText?: string
  themeName?: string
  themeIcon?: string
  themeKey?: string
}

export function QuestionCardEnhanced({
  question,
  selectedAnswer,
  onSelect,
  feedback,
  hintLevel,
  combo,
  questionIndex,
  totalQuestions,
  mode,
  lowHearts,
  xpFlyText,
  xpFlyKey,
  storyText,
  themeName,
  themeIcon,
  themeKey,
}: QuestionCardEnhancedProps) {
  const [encMsg, setEncMsg] = useState<EncMsg | null>(null)
  const [animKey, setAnimKey] = useState(0)

  // Show encouragement on new question
  useEffect(() => {
    setAnimKey(k => k + 1)
    if (!feedback) {
      const msgs = ENCOURAGEMENTS
      setEncMsg(msgs[Math.floor(Math.random() * msgs.length)])
    }
  }, [question?.question_id])

  // Show result message
  useEffect(() => {
    if (feedback) {
      const msgs = feedback.is_correct ? CORRECT_MSGS : WRONG_MSGS
      setEncMsg(msgs[Math.floor(Math.random() * msgs.length)])
    }
  }, [feedback])

  const isCorrect = feedback?.is_correct ?? null
  const typeLabel = question?.question_type === 'multiple_choice' ? '选择题' : '填空题'
  const levelEmoji = (question?.level || 1) === 1 ? '⭐' : '🌟🌟'
  const themeStyle = getThemeStyle(themeKey)
  const categoryColors: Record<string, string> = {
    quiz: themeStyle.card,
    diagnose: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
  }

  return (
    <div key={animKey} className="animate-question-enter space-y-3">
      {/* Theme header + story dialogue bubble */}
      {storyText && themeName && (
        <div className="animate-bubble-in space-y-2">
          <div className="flex items-center gap-2 px-2">
            <span className="text-xl">{themeIcon || '🎯'}</span>
            <span className={`text-xs font-semibold uppercase tracking-wider ${themeStyle.accent}`}>
              {themeName}
            </span>
          </div>
          <div className="flex items-start gap-2 px-1">
            <div className="bg-slate-800/90 rounded-2xl rounded-tl-sm px-4 py-3 border border-slate-600/50 shadow-lg">
              <p className="text-white text-sm leading-relaxed whitespace-pre-wrap">{storyText}</p>
            </div>
          </div>
        </div>
      )}

      {/* Encouragement bubble (only when no story) */}
      {!storyText && encMsg && (
        <div className="animate-bubble-in flex items-start gap-2 px-1" role="status">
          <span className="text-lg">{encMsg.emoji}</span>
          <div className="bg-slate-800/80 rounded-2xl rounded-tl-none px-3 py-2 border border-slate-700/50">
            <p className="text-slate-300 text-sm leading-relaxed">{encMsg.text}</p>
          </div>
        </div>
      )}

      {/* Question card */}
      <div className={`relative overflow-hidden rounded-2xl border bg-gradient-to-b ${categoryColors[mode]} ${
        themeKey ? themeStyle.border : 'border-blue-500/30'
      } ${
        isCorrect === true ? 'animate-correct-pulse border-green-500/50' :
        isCorrect === false ? 'ring-2 ring-orange-500 animate-wrong-shake' : ''
      }`}>
        {xpFlyText && (
          <div key={xpFlyKey} className="absolute top-4 right-4 z-20 animate-xp-fly text-green-400 font-bold text-lg drop-shadow-lg">
            {xpFlyText}
          </div>
        )}

        {/* Card header with badges */}
        <div className="flex items-center justify-between px-4 pt-3 pb-1">
          <div className="flex items-center gap-2">
            <span className="bg-slate-800/80 text-xs px-2.5 py-1 rounded-full text-slate-300 border border-slate-700/50">
              {typeLabel}
            </span>
            <span className="bg-slate-800/80 text-xs px-2.5 py-1 rounded-full text-amber-400 border border-slate-700/50">
              {levelEmoji} Lv.{question?.level || 1}
            </span>
          </div>
          {themeName && (
            <span className={`text-xs ${themeStyle.accent} truncate max-w-[120px]`}>
              {themeIcon} {themeName}
            </span>
          )}
          {!themeName && (
            <span className="text-xs text-slate-500 truncate max-w-[120px]">
              {question?.kp_name || ''}
            </span>
          )}
        </div>

        {/* Question text */}
        <div className="px-4 py-3">
          <MathText text={question?.question || ''} className="text-base" />
        </div>

        {/* Answer area */}
        <div className="px-4 pb-3">
          {question?.question_type === 'multiple_choice' && question?.options ? (
            <MultipleChoiceOptions
              options={question.options}
              selectedAnswer={selectedAnswer}
              onSelect={(opt) => !feedback && onSelect(opt)}
              disabled={!!feedback}
              feedback={feedback}
            />
          ) : (
            <AnswerInput
              value={selectedAnswer ?? ''}
              onChange={(v) => onSelect(v)}
              disabled={!!feedback}
            />
          )}
        </div>

        {/* Feedback */}
        {feedback && (
          <div className="px-4 pb-3">
            <FeedbackPanel
              isCorrect={isCorrect}
              hint={feedback?.hint}
              explanation={feedback && !isCorrect ? feedback.explanation : null}
              hintLevel={hintLevel}
              xpEarned={feedback?.xp_earned}
              combo={combo}
            />
          </div>
        )}

        {/* Low hearts warning */}
        {!feedback && lowHearts && (
          <div className="px-4 pb-3">
            <div className="text-center text-red-400/80 text-xs py-2 animate-pulse border border-red-500/20 rounded-lg bg-red-500/5" role="alert">
              ⚠️ 最后一次机会，仔细作答！
            </div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      {totalQuestions && totalQuestions > 0 && (
        <div className="px-1">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1.5">
            <span>学习进度</span>
            <span className="font-mono">{questionIndex}/{totalQuestions}</span>
          </div>
          <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-amber-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, (questionIndex / totalQuestions) * 100)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
