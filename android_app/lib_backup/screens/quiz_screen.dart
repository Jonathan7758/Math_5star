import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../api/api_client.dart';
import '../widgets/question_card.dart';
import '../game/math_sprite.dart';

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  final _api = ApiClient();
  Map<String, dynamic>? _question;
  String? _selectedAnswer;
  Map<String, dynamic>? _feedback;
  bool _loading = false;
  int _combo = 0;
  int _hearts = 3;
  int _xp = 0;

  @override
  void initState() {
    super.initState();
    _fetchQuestion();
  }

  Future<void> _fetchQuestion() async {
    setState(() => _loading = true);
    try {
      final q = await _api.getNextQuestion();
      setState(() { _question = q; _selectedAnswer = null; _feedback = null; _loading = false; });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    if (_selectedAnswer == null || _question == null) return;
    setState(() => _loading = true);
    try {
      final result = await _api.submitAnswer(questionId: _question!['question_id'], answer: _selectedAnswer!);
      final isCorrect = result['is_correct'] == true;
      if (isCorrect) {
        _combo++;
        final reward = await _api.processReward(true, _combo);
        setState(() { _xp = reward['total_xp'] ?? _xp; });
      } else {
        _combo = 0;
        if (!(result['should_retry'] == true)) {
          _hearts--;
        }
        await _api.processReward(false, 0);
      }
      setState(() { _feedback = result; _loading = false; });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_hearts <= 0) {
      return Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('💔', style: TextStyle(fontSize: 64)),
              const SizedBox(height: 16),
              const Text('今天的练习结束了', style: TextStyle(color: Colors.white, fontSize: 20)),
              const SizedBox(height: 8),
              Text('获得 XP: $_xp', style: const TextStyle(color: Color(0xFFFBBF24), fontSize: 16)),
              const SizedBox(height: 24),
              ElevatedButton(onPressed: () => Navigator.pop(context), child: const Text('返回')),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: Text('自由练习', style: const TextStyle(fontSize: 18)),
        actions: [
          // Hearts
          ...List.generate(3, (i) => Padding(
            padding: const EdgeInsets.only(right: 4),
            child: Text(i < _hearts ? '❤️' : '🖤', style: const TextStyle(fontSize: 18)),
          )),
          const SizedBox(width: 8),
          if (_combo >= 3)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: _combo >= 10 ? const Color(0x30FBBF24) : const Color(0x30A855F7),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text('🔥 $_combo连击', style: TextStyle(color: _combo >= 10 ? const Color(0xFFFBBF24) : const Color(0xFFA78BFA), fontSize: 12)),
            ),
          const SizedBox(width: 8),
        ],
      ),
      body: _question == null
          ? const Center(child: CircularProgressIndicator())
          : _buildQuestionView(),
    );
  }

  Widget _buildQuestionView() {
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: QuestionCard(
              question: _question!,
              selectedAnswer: _selectedAnswer,
              onSelect: _feedback == null ? (a) => setState(() => _selectedAnswer = a) : null,
              feedback: _feedback,
              isCorrect: _feedback?['is_correct'],
            ),
          ),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: _feedback == null
                ? SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: (_selectedAnswer != null && !_loading) ? _submit : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF59E0B),
                        foregroundColor: Colors.white,
                        disabledBackgroundColor: const Color(0x30334455),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: Text(_loading ? '检查中...' : '提交答案', style: const TextStyle(fontSize: 16)),
                    ),
                  )
                : SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _fetchQuestion,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _feedback?['is_correct'] == true ? const Color(0xFF22C55E) : const Color(0xFFF59E0B),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: Text(
                        _feedback?['is_correct'] == true ? '下一题 ✨' : (_feedback?['should_retry'] == true ? '再试一次 🔄' : '下一题'),
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
          ),
        ),
      ],
    );
  }
}
