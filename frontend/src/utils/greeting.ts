const TIME_GREETINGS: { start: number; end: number; greeting: string; emoji: string }[] = [
  { start: 6, end: 12, greeting: '早安！今天的数学冒险开始啦～', emoji: '🌅' },
  { start: 12, end: 18, greeting: '下午好！来活动一下大脑吧！', emoji: '☀️' },
  { start: 18, end: 22, greeting: '晚上好！睡前做几题，知识记得牢～', emoji: '🌙' },
  { start: 22, end: 24, greeting: '夜深了，做完题早点休息哦～', emoji: '🌟' },
  { start: 0, end: 6, greeting: '这么晚了还在学习，真厉害！', emoji: '✨' },
]

export function getTimeGreeting(): { text: string; emoji: string } {
  const hour = new Date().getHours()
  const match = TIME_GREETINGS.find(g => hour >= g.start && hour < g.end)
  if (match) return { text: match.greeting, emoji: match.emoji }
  return { text: TIME_GREETINGS[0].greeting, emoji: TIME_GREETINGS[0].emoji }
}
