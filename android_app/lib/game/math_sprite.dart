import 'package:flame/components.dart';
import 'package:flame/effects.dart';
import 'package:flame/game.dart';
import 'package:flutter/material.dart';
import 'dart:math';

enum SpriteReaction { idle, happy, celebrate, excited, encourage, thinking }

class MathSprite extends PositionComponent {
  MathSprite({
    Vector2? position,
  }) : super(position: position ?? Vector2(60, 50), size: Vector2(80, 90), anchor: Anchor.center);

  SpriteReaction _reaction = SpriteReaction.idle;
  int _stage = 0;
  double _bobAngle = 0;
  final List<_Sparkle> _sparkles = [];

  void setReaction(SpriteReaction reaction) {
    _reaction = reaction;
    if (reaction == SpriteReaction.celebrate) _spawnSparkles();
  }

  void setStage(int stage) => _stage = stage;

  void doBounce() {
    add(ScaleEffect.to(
      Vector2(0.85, 0.85),
      EffectController(duration: 0.1, reverseDuration: 0.1),
    ));
  }

  void _spawnSparkles() {
    for (int i = 0; i < 12; i++) {
      final angle = (i / 12) * 2 * pi;
      _sparkles.add(_Sparkle(
        offset: Offset(cos(angle) * 40, sin(angle) * 40),
        color: const Color.fromARGB(255, 251, 191, 36),
        delay: i * 0.05,
      ));
    }
  }

  @override
  void update(double dt) {
    super.update(dt);
    _bobAngle += dt * 2;
    _sparkles.removeWhere((s) => s.life <= 0);
    for (final s in _sparkles) { s.update(dt); }
  }

  @override
  void render(Canvas canvas) {
    canvas.save();
    canvas.translate(size.x / 2, size.y / 2);
    final bobY = sin(_bobAngle) * 4;
    canvas.translate(0, bobY);
    _drawSprite(canvas, _stage);
    for (final s in _sparkles) {
      canvas.save();
      canvas.translate(s.offset.dx, s.offset.dy);
      final paint = Paint()..color = s.color.withAlpha((220 * s.life).toInt());
      canvas.drawCircle(Offset.zero, 4 * s.life, paint);
      canvas.restore();
    }
    canvas.restore();
  }

  void _drawSprite(Canvas canvas, int stage) {
    final bodyPaint = Paint()
      ..shader = RadialGradient(
        colors: const [Color(0xFFFBBF24), Color(0xFFD97706)],
      ).createShader(Rect.fromCircle(center: Offset.zero, radius: 40));
    final glowPaint = Paint()..color = const Color(0xFFFEF3C7).withAlpha(100);

    canvas.drawCircle(Offset.zero, 35, bodyPaint);
    canvas.drawCircle(Offset.zero, 25, glowPaint);

    final eyePaint = Paint()..color = Colors.white;
    canvas.drawCircle(const Offset(-10, -5), 6, eyePaint);
    canvas.drawCircle(const Offset(10, -5), 6, eyePaint);
    final pupilPaint = Paint()..color = const Color(0xFF1E293B);
    canvas.drawCircle(const Offset(-9, -4), 3, pupilPaint);
    canvas.drawCircle(const Offset(11, -4), 3, pupilPaint);

    final mouthPaint = Paint()
      ..color = const Color(0xFF1E293B)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    final mouthPath = Path();
    switch (_reaction) {
      case SpriteReaction.happy:
      case SpriteReaction.celebrate:
      case SpriteReaction.excited:
        mouthPath.arcTo(Rect.fromCircle(center: const Offset(0, 8), radius: 8), pi * 0.2, pi * 0.6, false);
      case SpriteReaction.encourage:
        mouthPath.moveTo(-6, 10); mouthPath.lineTo(6, 10);
      case SpriteReaction.thinking:
        mouthPath.moveTo(-5, 10); mouthPath.quadraticBezierTo(0, 5, 5, 10);
      case SpriteReaction.idle:
        mouthPath.moveTo(-4, 10); mouthPath.quadraticBezierTo(0, 6, 4, 10);
    }
    canvas.drawPath(mouthPath, mouthPaint);

    if (stage >= 1) {
      final leafPaint = Paint()..color = const Color(0xFF22C55E).withAlpha(180);
      canvas.drawPath(Path()..moveTo(0, -35)..quadraticBezierTo(-20, -55, -25, -45)..quadraticBezierTo(-10, -40, 0, -35), leafPaint);
      canvas.drawPath(Path()..moveTo(0, -35)..quadraticBezierTo(20, -55, 25, -45)..quadraticBezierTo(10, -40, 0, -35), leafPaint);
    }
    if (stage >= 3) {
      final symPaint = Paint()..color = const Color(0xFFFBBF24).withAlpha(150);
      _drawText(canvas, 'pi', const Offset(-45, -35), symPaint, 14);
      _drawText(canvas, 'sum', const Offset(40, -30), symPaint, 12);
      _drawText(canvas, 'infinity', const Offset(35, 25), symPaint, 12);
    }
    if (stage >= 4) {
      final starPaint = Paint()..color = const Color(0xFFFCD34D);
      canvas.drawPath(_starPath(size: 12, center: const Offset(0, -42)), starPaint);
    }
  }

  Path _starPath({required double size, required Offset center}) {
    final path = Path();
    for (int i = 0; i < 5; i++) {
      final angle = (i * 72 - 90) * pi / 180;
      final outer = Offset(center.dx + cos(angle) * size, center.dy + sin(angle) * size);
      final innerAngle = ((i * 72 + 36) - 90) * pi / 180;
      final inner = Offset(center.dx + cos(innerAngle) * size * 0.4, center.dy + sin(innerAngle) * size * 0.4);
      if (i == 0) path.moveTo(outer.dx, outer.dy);
      path.lineTo(inner.dx, inner.dy);
      path.lineTo(outer.dx, outer.dy);
    }
    path.close();
    return path;
  }

  void _drawText(Canvas canvas, String text, Offset offset, Paint paint, double fontSize) {
    final builder = TextPainter(
      text: TextSpan(text: text, style: TextStyle(color: const Color(0xFFFBBF24), fontSize: fontSize, fontStyle: FontStyle.italic)),
      textDirection: TextDirection.ltr,
    );
    builder.layout();
    builder.paint(canvas, offset);
  }
}

class _Sparkle {
  Offset offset;
  Color color;
  double delay;
  double life = 1.0;
  double elapsed = 0;
  _Sparkle({required this.offset, required this.color, required this.delay});
  void update(double dt) { elapsed += dt; if (elapsed < delay) return; life -= dt * 3; }
}

// Widget wrapper with tap handling
class SpriteGameWidget extends StatelessWidget {
  final MathSprite sprite;
  final VoidCallback? onTap;

  const SpriteGameWidget({super.key, required this.sprite, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        sprite.doBounce();
        onTap?.call();
      },
      child: GameWidget(game: _SpriteGame(sprite)),
    );
  }
}

class _SpriteGame extends FlameGame {
  final MathSprite sprite;
  _SpriteGame(this.sprite);
  @override
  Future<void> onLoad() async { add(sprite); }
}
