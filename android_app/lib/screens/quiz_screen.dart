import 'package:flutter/material.dart';
import '../api/api_client.dart';
import '../widgets/question_card.dart';
import '../utils/sound.dart';

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
  String? _storyQuestion;
  String? _themeIcon;

  @override
  void initState() { super.initState(); _fetchQuestion(); }

  Future<void> _fetchQuestion() async {
    setState(() => _loading = true);
    try {
      final q = await _api.getNextQuestion();
      setState(() { _question = q; _selectedAnswer = null; _feedback = null; _loading = false; });
      _loadStory(q);
    } catch (_) { setState(() => _loading = false); }
  }

  Future<void> _loadStory(Map<String, dynamic> q) async {
    try {
      final story = await _api.post('/api/exercise/story', {'question_id': q['question_id'], 'question_text': q['question']});
      if (mounted) setState(() { _storyQuestion = story['story_question']; _themeIcon = story['theme_icon']; });
    } catch (_) {}
  }

  Future<void> _submit() async {
    if (_selectedAnswer == null || _question == null) return;
    setState(() => _loading = true);
    try {
      final result = await _api.submitAnswer(questionId: _question!['question_id'], answer: _selectedAnswer!);
      final isCorrect = result['is_correct'] == true;
      if (isCorrect) { _combo++; await _api.processReward(true, _combo); GameSound.correct(); }
      else { _combo = 0; if (result['should_retry'] != true) _hearts--; await _api.processReward(false, 0); GameSound.incorrect(); }
      setState(() { _feedback = result; _loading = false; });
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    if (_hearts <= 0) {
      return Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        body: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Text('\u{1F494}', style: TextStyle(fontSize: 64)),
          const SizedBox(height: 16),
          const Text('\u{4ECA}\u{5929}\u{7684}\u{7EC3}\u{4E60}\u{7ED3}\u{675F}\u{4E86}', style: TextStyle(color: Colors.white, fontSize: 20)),
          const SizedBox(height: 8),
          Text('\u{83B7}\u{5F97} XP: $_xp', style: const TextStyle(color: Color(0xFFFBBF24), fontSize: 16)),
          const SizedBox(height: 24),
          Semantics(label: '\u{8FD4}\u{56DE}', child: ElevatedButton(onPressed: () => Navigator.pop(context), child: const Text('\u{8FD4}\u{56DE}'))),
        ])),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('\u{81EA}\u{7531}\u{7EC3}\u{4E60}', style: TextStyle(fontSize: 18)),
        actions: [
          ...List.generate(3, (i) => Padding(padding: const EdgeInsets.only(right: 4), child: Text(i < _hearts ? '\u{2764}\u{FE0F}' : '\u{1F5A4}', style: const TextStyle(fontSize: 18)))),
          const SizedBox(width: 8),
          if (_combo >= 3)
            Container(
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(color: _combo >= 10 ? const Color(0x30FBBF24) : const Color(0x30A855F7), borderRadius: BorderRadius.circular(10)),
              child: Text('\u{1F525} $_combo\u{8FDE}\u{51FB}', style: TextStyle(color: _combo >= 10 ? const Color(0xFFFBBF24) : const Color(0xFFA78BFA), fontSize: 12)),
            ),
        ],
      ),
      body: _question == null
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFF59E0B)))
          : _buildQuestionView(),
    );
  }

  Widget _buildQuestionView() {
    final isCorrect = _feedback?['is_correct'];
    return Column(children: [
      Expanded(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: QuestionCard(
            question: _question!,
            selectedAnswer: _selectedAnswer,
            onSelect: _feedback == null ? (a) => setState(() => _selectedAnswer = a) : null,
            feedback: _feedback,
            isCorrect: isCorrect,
            storyQuestion: _storyQuestion,
            themeIcon: _themeIcon,
          ),
        ),
      ),
      SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: _feedback == null
              ? Semantics(
                  label: '提交答案',
                  child: SizedBox(
                    width: double.infinity, height: 52,
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
                  ),
                )
              : Semantics(
                  label: isCorrect == true ? '下一题' : '再试一次',
                  child: SizedBox(
                    width: double.infinity, height: 52,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _fetchQuestion,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isCorrect == true ? const Color(0xFF22C55E) : const Color(0xFFF59E0B),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: Text(
                        isCorrect == true ? '下一题' : (_feedback?['should_retry'] == true ? '再试一次' : '下一题'),
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                ),
        ),
      ),
    ]);
  }
}
