import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class QuestionCard extends StatelessWidget {
  final Map<String, dynamic> question;
  final String? selectedAnswer;
  final void Function(String)? onSelect;
  final Map<String, dynamic>? feedback;
  final bool? isCorrect;

  const QuestionCard({
    super.key,
    required this.question,
    this.selectedAnswer,
    this.onSelect,
    this.feedback,
    this.isCorrect,
  });

  @override
  Widget build(BuildContext context) {
    final options = (question['options'] as List?)?.cast<String>() ?? [];
    final isMulti = options.isNotEmpty;
    final level = question['level'] ?? 1;
    final kpName = question['kp_name'] ?? '';

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF7C3AED).withAlpha(30),
            const Color(0xFF0F172A),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: isCorrect == true
              ? const Color(0x8022C55E)
              : isCorrect == false
                  ? const Color(0x80EF4444)
                  : const Color(0x30334455),
          width: isCorrect != null ? 2 : 1,
        ),
        boxShadow: isCorrect == true
            ? [BoxShadow(color: const Color(0xFF22C55E).withAlpha(30), blurRadius: 20, spreadRadius: 2)]
            : null,
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Badges row
            Row(
              children: [
                _Badge(text: isMulti ? '选择题' : '填空题', color: const Color(0xFF475569)),
                const SizedBox(width: 8),
                _Badge(text: 'Lv.$level ${'⭐' * (level as int)}', color: const Color(0xFFD97706).withAlpha(60)),
                const Spacer(),
                Text(kpName, style: TextStyle(color: Colors.grey[600], fontSize: 11)),
              ],
            ),

            const SizedBox(height: 16),

            // Question text
            Text(
              question['question'] ?? '',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 17,
                height: 1.6,
                fontWeight: FontWeight.w500,
              ),
            ),

            const SizedBox(height: 20),

            // Options
            if (isMulti)
              ...options.asMap().entries.map((e) {
                final opt = e.value;
                final isSelected = selectedAnswer == opt;
                final isCorrectOpt = feedback != null && feedback?['correct_answer'] == opt;
                final isWrongSelected = feedback != null && isSelected && feedback?['is_correct'] == false;

                Color bgColor = const Color(0x101E293B);
                Color borderColor = const Color(0x20334455);
                Color textColor = const Color(0xFFCBD5E1);

                if (isWrongSelected) {
                  bgColor = const Color(0x30EF4444);
                  borderColor = const Color(0x80EF4444);
                  textColor = const Color(0xFFFCA5A5);
                } else if (isCorrectOpt) {
                  bgColor = const Color(0x3022C55E);
                  borderColor = const Color(0x8022C55E);
                  textColor = const Color(0xFF86EFAC);
                } else if (isSelected && feedback == null) {
                  bgColor = const Color(0x30F59E0B);
                  borderColor = const Color(0x80F59E0B);
                  textColor = const Color(0xFFFCD34D);
                }

                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: GestureDetector(
                    onTap: onSelect != null ? () => onSelect!(opt) : null,
                    child: AnimatedContainer(
                      duration: 200.ms,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: bgColor,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: borderColor),
                      ),
                      child: Text(
                        opt,
                        style: TextStyle(color: textColor, fontSize: 15),
                      ),
                    ),
                  ),
                ).animate().slideX(begin: 0.03 * (e.key + 1), end: 0, duration: 300.ms);
              })
            else ...[
              // Text input
              TextField(
                style: const TextStyle(color: Colors.white, fontSize: 18),
                textAlign: TextAlign.center,
                decoration: InputDecoration(
                  hintText: '输入答案...',
                  hintStyle: TextStyle(color: Colors.grey[600]),
                  filled: true,
                  fillColor: const Color(0x101E293B),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0x30334455)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0x30334455)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFFF59E0B)),
                  ),
                ),
                enabled: onSelect != null,
                onChanged: onSelect,
              ),
            ],

            // Feedback section
            if (feedback != null) ...[
              const SizedBox(height: 16),
              if (isCorrect == true)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0x1522C55E),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0x3022C55E)),
                  ),
                  child: const Row(
                    children: [
                      Text('🎉', style: TextStyle(fontSize: 18)),
                      SizedBox(width: 8),
                      Text('正确！', style: TextStyle(color: Color(0xFF4ADE80), fontSize: 15, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ).animate().scale(duration: 300.ms, begin: const Offset(0.95, 0.95), end: const Offset(1, 1)),
              if (feedback?['hint'] != null && isCorrect != true)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0x15F59E0B),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0x30F59E0B)),
                  ),
                  child: Row(
                    children: [
                      const Text('💡', style: TextStyle(fontSize: 18)),
                      const SizedBox(width: 8),
                      Expanded(child: Text(feedback!['hint'] ?? '', style: const TextStyle(color: Color(0xFFFCD34D), fontSize: 14))),
                    ],
                  ),
                ),
              if (feedback?['explanation'] != null && isCorrect != true)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0x101E293B),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      feedback!['explanation'] ?? '',
                      style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                    ),
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String text;
  final Color color;
  const _Badge({required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(text, style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 11)),
    );
  }
}
