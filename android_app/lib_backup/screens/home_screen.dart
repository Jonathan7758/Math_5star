import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../game/math_sprite.dart';
import '../api/api_client.dart';
import '../api/api_config.dart';
import 'diagnose_screen.dart';
import 'quiz_screen.dart';
import 'parent_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  late final MathSprite _sprite;
  final _api = ApiClient();
  Map<String, dynamic>? _rewards;
  String _greeting = '';
  String _greetingEmoji = '';
  List<String> _spriteMessages = [];
  int _tapCount = 0;

  final _messages = [
    '嗨！我是启小星~',
    '你今天真棒！加油！',
    '每道题都是成长的机会！',
    '数学很有意思对吧？',
    '我会一直陪着你的！',
    '答对题目我就能长大啦~',
    '一起点亮知识的星空吧！',
  ];

  @override
  void initState() {
    super.initState();
    _setGreeting();
    _loadRewards();
    _sprite = MathSprite(
      onTap: _onSpriteTap,
    );
  }

  void _setGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 6) {
      _greeting = '这么晚了还在学习，真厉害！'; _greetingEmoji = '✨';
    } else if (hour < 12) {
      _greeting = '早安！今天的数学冒险开始啦~'; _greetingEmoji = '🌅';
    } else if (hour < 18) {
      _greeting = '下午好！来活动一下大脑吧！'; _greetingEmoji = '☀️';
    } else {
      _greeting = '晚上好！睡前做几题，知识记得牢~'; _greetingEmoji = '🌙';
    }
  }

  Future<void> _loadRewards() async {
    try {
      final data = await _api.getRewardsStatus();
      if (mounted) setState(() => _rewards = data);
    } catch (_) {}
  }

  void _onSpriteTap() {
    setState(() {
      _spriteMessages = [
        _messages[_tapCount % _messages.length],
      ];
      _tapCount++;
    });
    _sprite.setReaction(SpriteReaction.celebrate);
    Future.delayed(const Duration(milliseconds: 800), () {
      _sprite.setReaction(SpriteReaction.idle);
    });
  }

  @override
  Widget build(BuildContext context) {
    final level = _rewards?['level'] ?? 1;
    final xpCurrent = _rewards?['xp_current'] ?? 0;
    final xpNext = _rewards?['xp_next'] ?? 100;
    final starCoins = _rewards?['star_coins'] ?? 0;
    final streakDays = _rewards?['streak_days'] ?? 0;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // --- Greeting ---
              Text(
                '$_greetingEmoji $_greeting',
                style: const TextStyle(color: Color(0xFFFBBF24), fontSize: 14),
              ).animate().fadeIn(duration: 400.ms).slideY(begin: -0.1, end: 0),

              const SizedBox(height: 16),

              // --- Sprite ---
              SizedBox(
                height: 160,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    SpriteGameWidget(sprite: _sprite),
                    // Sprite messages
                    ..._spriteMessages.asMap().entries.map((e) {
                      return Positioned(
                        top: 0,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xEE1E293B),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0x80334455)),
                          ),
                          child: Text(
                            e.value,
                            style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 13),
                          ),
                        ),
                      ).animate(key: ValueKey(e.key)).scale(duration: 300.ms, begin: const Offset(0.8, 0.8), end: const Offset(1, 1));
                    }),
                  ],
                ),
              ),

              const SizedBox(height: 8),

              // --- Stats bar ---
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _StatChip(icon: '⭐', label: 'Lv.$level'),
                  const SizedBox(width: 12),
                  _StatChip(icon: '💰', label: '$starCoins'),
                  const SizedBox(width: 12),
                  _StatChip(icon: '🔥', label: '$streakDays天'),
                ],
              ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

              const SizedBox(height: 12),

              // --- XP Bar ---
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: xpNext > 0 ? xpCurrent / xpNext : 0,
                  minHeight: 10,
                  backgroundColor: const Color(0x30334455),
                  color: const Color(0xFFF59E0B),
                ),
              ).animate().fadeIn(delay: 300.ms, duration: 500.ms),

              const SizedBox(height: 20),

              // --- Action Grid ---
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.3,
                children: [
                  _ActionCard(
                    icon: '🔍',
                    title: '开始诊断',
                    subtitle: '找出薄弱点',
                    color: const Color(0xFF7C3AED),
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const DiagnoseScreen())),
                    index: 0,
                  ),
                  _ActionCard(
                    icon: '✏️',
                    title: '自由练习',
                    subtitle: '刷题赚XP',
                    color: const Color(0xFF2563EB),
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const QuizScreen())),
                    index: 1,
                  ),
                  _ActionCard(
                    icon: '📊',
                    title: '家长看板',
                    subtitle: '查看进度',
                    color: const Color(0xFF059669),
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ParentScreen())),
                    index: 2,
                  ),
                  _ActionCard(
                    icon: '🏆',
                    title: '成就徽章',
                    subtitle: '30种成就',
                    color: const Color(0xFFD97706),
                    onTap: () {},
                    index: 3,
                  ),
                ],
              ),

              const SizedBox(height: 6),

              Text(
                '每天10分钟 · 点亮知识的星空',
                style: TextStyle(color: Colors.grey[600], fontSize: 11),
              ).animate().fadeIn(delay: 600.ms),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String icon;
  final String label;
  const _StatChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0x201E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x30334455)),
      ),
      child: Text('$icon $label', style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 13)),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final String icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;
  final int index;

  const _ActionCard({
    required this.icon, required this.title, required this.subtitle,
    required this.color, required this.onTap, required this.index,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: 200.ms,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [color.withAlpha(40), color.withAlpha(10)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withAlpha(80)),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(icon, style: const TextStyle(fontSize: 32)),
            const SizedBox(height: 6),
            Text(title, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(subtitle, style: TextStyle(color: Colors.grey[500], fontSize: 11)),
          ],
        ),
      ),
    )
        .animate(delay: (100 * index).ms)
        .fadeIn(duration: 400.ms)
        .slideY(begin: 0.2, end: 0);
  }
}
