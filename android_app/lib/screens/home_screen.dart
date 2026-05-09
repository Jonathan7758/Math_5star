import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../game/math_sprite.dart';
import '../api/api_client.dart';
import '../api/api_config.dart';
import 'diagnose_screen.dart';
import 'quiz_screen.dart';
import 'parent_screen.dart';
import 'settings_screen.dart';

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
  String? _spriteMsg;
  int _tapCount = 0;
  bool _showLoading = true;

  final _messages = [
    '嗨！我是启小星~', '你今天真棒！加油！', '每道题都是成长的机会！',
    '数学很有意思对吧？', '我会一直陪着你的！', '答对题目我就能长大啦~',
    '一起点亮知识的星空吧！',
  ];

  @override
  void initState() {
    super.initState();
    _setGreeting();
    _loadRewards();
    _sprite = MathSprite();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _sprite.setReaction(SpriteReaction.happy);
      Future.delayed(const Duration(seconds: 1), () => _sprite.setReaction(SpriteReaction.idle));
    });
  }

  void _setGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 6) { _greeting = '这么晚了还在学习，真厉害！'; _greetingEmoji = '✨'; }
    else if (hour < 12) { _greeting = '早安！今天的数学冒险开始啦~'; _greetingEmoji = '🌅'; }
    else if (hour < 18) { _greeting = '下午好！来活动一下大脑吧！'; _greetingEmoji = '☀️'; }
    else { _greeting = '晚上好！睡前做几题，知识记得牢~'; _greetingEmoji = '🌙'; }
  }

  Future<void> _loadRewards() async {
    try {
      final data = await _api.getRewardsStatus();
      if (mounted) setState(() { _rewards = data; _showLoading = false; });
    } catch (_) {
      if (mounted) setState(() => _showLoading = false);
    }
  }

  void _onSpriteTap() {
    setState(() => _spriteMsg = _messages[_tapCount % _messages.length]);
    _tapCount++;
    _sprite.setReaction(SpriteReaction.celebrate);
    _sprite.doBounce();
    Future.delayed(const Duration(milliseconds: 800), () => _sprite.setReaction(SpriteReaction.idle));
    Future.delayed(const Duration(seconds: 3), () { if (mounted) setState(() => _spriteMsg = null); });
  }

  @override
  Widget build(BuildContext context) {
    final level = _rewards?['level'] ?? 1;
    final xpCurrent = (_rewards?['xp_current'] ?? 0).toDouble();
    final xpNext = (_rewards?['xp_next'] ?? 100).toDouble();
    final starCoins = _rewards?['star_coins'] ?? 0;
    final streakDays = _rewards?['streak_days'] ?? 0;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: _showLoading
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 48, height: 48,
                    child: CircularProgressIndicator(color: Color(0xFFF59E0B), strokeWidth: 3),
                  ),
                  SizedBox(height: 16),
                  Text('加载中...', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 14)),
                ],
              ),
            )
          : SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: constraints.maxHeight),
                child: Column(
                  children: [
                    // --- Greeting ---
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              '$_greetingEmoji $_greeting',
                              style: const TextStyle(color: Color(0xFFFBBF24), fontSize: 14),
                            ).animate().fadeIn(duration: 400.ms),
                          ),
                          GestureDetector(
                            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
                            child: const Icon(Icons.settings, color: Color(0xFF64748B), size: 22),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // --- Sprite + message bubble ---
                    Stack(
                      alignment: Alignment.topCenter,
                      children: [
                        SizedBox(
                          height: 140,
                          width: double.infinity,
                          child: SpriteGameWidget(sprite: _sprite, onTap: _onSpriteTap),
                        ),
                        if (_spriteMsg != null)
                          Positioned(
                            top: 0,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                              decoration: BoxDecoration(
                                color: const Color(0xEE1E293B),
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: const Color(0x80334455)),
                              ),
                              child: Text(_spriteMsg!, style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 13)),
                            ),
                          ).animate().scale(duration: 300.ms, begin: const Offset(0.8, 0.8), end: const Offset(1, 1)),
                      ],
                    ),

                    // --- Stats bar ---
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          _StatChip(icon: '⭐', label: 'Lv.$level'),
                          const SizedBox(width: 10),
                          _StatChip(icon: '💰', label: '$starCoins'),
                          const SizedBox(width: 10),
                          _StatChip(icon: '🔥', label: '$streakDays天'),
                        ],
                      ).animate().fadeIn(delay: 200.ms),
                    ),

                    const SizedBox(height: 10),

                    // --- XP Bar ---
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: LinearProgressIndicator(
                          value: xpNext > 0 ? (xpCurrent / xpNext).clamp(0, 1) : 0,
                          minHeight: 10,
                          backgroundColor: const Color(0x30334455),
                          color: const Color(0xFFF59E0B),
                        ),
                      ).animate().fadeIn(delay: 300.ms),
                    ),

                    const SizedBox(height: 24),

                    // --- Action Grid ---
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(child: _ActionCard(icon: '🔍', title: '开始诊断', subtitle: '找出薄弱点', color: const Color(0xFF7C3AED), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const DiagnoseScreen()))).animate().fadeIn(delay: 100.ms)),
                              const SizedBox(width: 12),
                              Expanded(child: _ActionCard(icon: '✏️', title: '自由练习', subtitle: '刷题赚XP', color: const Color(0xFF2563EB), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const QuizScreen()))).animate().fadeIn(delay: 200.ms)),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(child: _ActionCard(icon: '📊', title: '家长看板', subtitle: '查看进度', color: const Color(0xFF059669), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ParentScreen()))).animate().fadeIn(delay: 300.ms)),
                              const SizedBox(width: 12),
                              Expanded(child: _ActionCard(icon: '🏆', title: '成就徽章', subtitle: '30种成就', color: const Color(0xFFD97706), onTap: null, disabled: true).animate().fadeIn(delay: 400.ms)),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    Text(
                      '每天10分钟 · 点亮知识的星空',
                      style: TextStyle(color: Colors.grey[600], fontSize: 11),
                    ).animate().fadeIn(delay: 500.ms),

                    const SizedBox(height: 16),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String icon; final String label;
  const _StatChip({required this.icon, required this.label});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: const Color(0x201E293B), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0x30334455))),
      child: Text('$icon $label', style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 13)),
    );
  }
}

class _ActionCard extends StatefulWidget {
  final String icon, title, subtitle;
  final Color color;
  final VoidCallback? onTap;
  final bool disabled;
  const _ActionCard({required this.icon, required this.title, required this.subtitle, required this.color, this.onTap, this.disabled = false});

  @override
  State<_ActionCard> createState() => _ActionCardState();
}

class _ActionCardState extends State<_ActionCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final effectiveColor = widget.disabled ? Colors.grey : widget.color;
    return GestureDetector(
      onTapDown: widget.disabled ? null : (_) => setState(() => _pressed = true),
      onTapUp: widget.disabled ? null : (_) => setState(() => _pressed = false),
      onTapCancel: widget.disabled ? null : () => setState(() => _pressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: _pressed ? 0.95 : 1.0,
        duration: const Duration(milliseconds: 100),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [effectiveColor.withAlpha(40), effectiveColor.withAlpha(10)],
              begin: Alignment.topLeft, end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: effectiveColor.withAlpha(widget.disabled ? 20 : 80)),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(widget.icon, style: TextStyle(fontSize: 32, color: widget.disabled ? Colors.grey[600] : null)),
              const SizedBox(height: 6),
              Text(widget.title, style: TextStyle(color: widget.disabled ? Colors.grey[500] : Colors.white, fontSize: 15, fontWeight: FontWeight.bold)),
              const SizedBox(height: 2),
              Text(widget.subtitle, style: TextStyle(color: widget.disabled ? Colors.grey[700] : Colors.grey[500], fontSize: 11)),
              if (widget.disabled) Text('即将开放', style: TextStyle(color: Colors.grey[700], fontSize: 9)),
            ],
          ),
        ),
      ),
    );
  }
}
