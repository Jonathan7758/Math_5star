import { useState } from 'react'

interface OnboardingProps {
  onComplete: () => void
}

const SLIDES = [
  {
    icon: '🌟',
    title: '欢迎来到数学启明星！',
    body: '我是你的学习伙伴启小星。每天花10分钟，我们一起探索数学的世界！答对题目可以获得XP和星币，让启小星茁壮成长。',
    highlight: '每天10分钟，轻松学数学',
  },
  {
    icon: '🔍',
    title: '先诊断，后学习',
    body: '点击"开始诊断"做几道测试题，系统会找到你最需要加强的知识点，然后生成专属学习路径。跟着路径一步步攻克薄弱环节！',
    highlight: '专属学习路径，精准提升',
  },
  {
    icon: '❤️',
    title: '每天3颗心，好好珍惜',
    body: '每道题答错且用完提示后，会消耗一颗心。3颗心用完今天的练习就结束啦！认真思考再作答，保持连胜还能解锁更多成就哦～',
    highlight: '用心作答，守护连胜！',
  },
]

export function Onboarding({ onComplete }: OnboardingProps) {
  const [slide, setSlide] = useState(0)

  const handleNext = () => {
    if (slide < SLIDES.length - 1) {
      setSlide((s) => s + 1)
    } else {
      localStorage.setItem('onboarding_done', '1')
      onComplete()
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 backdrop-blur-md">
      <div className="w-[90%] max-w-sm space-y-6 text-center animate-scale-in">
        <div className="text-7xl animate-bounce-slow">{SLIDES[slide].icon}</div>

        <h2 className="text-xl font-bold text-white">{SLIDES[slide].title}</h2>

        <div className="card space-y-3">
          <p className="text-slate-300 text-sm leading-relaxed">{SLIDES[slide].body}</p>
          <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg py-2 px-3">
            <p className="text-primary-300 text-xs font-medium">{SLIDES[slide].highlight}</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-center gap-2">
            {SLIDES.map((_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full transition-all ${
                  i === slide ? 'bg-primary-400 w-6' : 'bg-slate-600'
                }`}
              />
            ))}
          </div>

          <button onClick={handleNext} className="btn-primary w-full">
            {slide < SLIDES.length - 1 ? '下一步' : '开始冒险！'}
          </button>

          {slide < SLIDES.length - 1 && (
            <button
              onClick={() => { localStorage.setItem('onboarding_done', '1'); onComplete() }}
              className="text-slate-500 text-xs"
            >
              跳过引导
            </button>
          )}

          <p className="text-slate-600 text-xs">
            {slide + 1} / {SLIDES.length}
          </p>
        </div>
      </div>
    </div>
  )
}
