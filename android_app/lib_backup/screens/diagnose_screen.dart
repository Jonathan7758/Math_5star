import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../api/api_client.dart';
import '../api/api_config.dart';
import '../widgets/question_card.dart';

class DiagnoseScreen extends StatefulWidget {
  const DiagnoseScreen({super.key});

  @override
  State<DiagnoseScreen> createState() => _DiagnoseScreenState();
}

class _DiagnoseScreenState extends State<DiagnoseScreen> {
  final _api = ApiClient();
  Map<String, dynamic>? _question;
  String? _selectedAnswer;
  Map<String, dynamic>? _feedback;
  bool _loading = false;
  final _records = <Map<String, dynamic>>[];
  int _questionIndex = 0;
  String _encMsg = '';
  String _encEmoji = '';

  final _encouragements = [
    {'text': '仔细读题，你一定可以的！', 'emoji': '💪'},
    {'text': '先理解题目再作答哦~', 'emoji': '🤔'},
    {'text': '遇到计算题一步一步来！', 'emoji': '📝'},
    {'text': '别着急，慢慢想~', 'emoji': '🌟'},
  ];

  @override
  void initState() {
    super.initState();
    _showEncouragement();
  }

  void _showEncouragement() {
    final m = (_encouragements..shuffle()).first;
    setState(() { _encMsg = m['text']!; _encEmoji = m['emoji']!; });
  }

  Future<void> _fetchQuestion() async {
    setState(() => _loading = true);
    try {
      final q = await _api.getNextQuestion();
      setState(() {
        _question = q;
        _selectedAnswer = null;
        _feedback = null;
        _loading = false;
      });
      _showEncouragement();
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    if (_selectedAnswer == null || _question == null) return;
    setState(() => _loading = true);
    try {
      final result = await _api.submitAnswer(
        questionId: _question!['question_id'],
        answer: _selectedAnswer!,
      );
      setState(() {
        _feedback = result;
        _loading = false;
        _questionIndex++;
      });
      _records.add({
        'kp_id': _question!['knowledge_point_id'],
        'is_correct': result['is_correct'],
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _finishDiagnose() async {
    if (_records.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请至少回答3题')),
      );
      return;
    }
    setState(() => _loading = true);
    try {
      final report = await _api.submitDiagnose(_records);
      if (mounted) {
        Navigator.pop(context, report);
      }
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('知识诊断'),
        actions: [
          TextButton(
            onPressed: _records.length >= 3 ? _finishDiagnose : null,
            child: Text('完成(${_records.length})', style: TextStyle(color: _records.length >= 3 ? const Color(0xFFFBBF24) : Colors.grey))),
        ],
      ),
      body: _question == null ? _buildStartScreen() : _buildQuestionScreen(),
    );
  }

  Widget _buildStartScreen() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('🔍', style: TextStyle(fontSize: 64)),
            const SizedBox(height: 16),
            const Text('准备好了吗？', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('系统会根据你的答题情况，找出薄弱环节', style: TextStyle(color: Colors.grey, fontSize: 14)),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _loading ? null : _fetchQuestion,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF59E0B),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                child: Text(_loading ? '加载中...' : '开始诊断', style: const TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0),
      ),
    );
  }

  Widget _buildQuestionScreen() {
    final isCorrect = _feedback?['is_correct'];

    return Column(
      children: [
        // Encouragement bubble
        if (_encMsg.isNotEmpty && _feedback == null)
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xCC1E293B),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Text(_encEmoji, style: const TextStyle(fontSize: 18)),
                const SizedBox(width: 8),
                Text(_encMsg, style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 14)),
              ],
            ),
          ).animate().fadeIn(duration: 300.ms),

        // Question card
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: QuestionCard(
              question: _question!,
              selectedAnswer: _selectedAnswer,
              onSelect: (a) => !_feedbackIsActive ? setState(() => _selectedAnswer = a) : null,
              feedback: _feedback,
              isCorrect: isCorrect,
            ).animate(key: ValueKey(_question?['question_id']))
              .fadeIn(duration: 400.ms)
              .slideY(begin: 0.05, end: 0),
          ),
        ),

        // Action buttons
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: _feedbackIsActive
                ? Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: _loading ? null : _fetchQuestion,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: isCorrect == true ? const Color(0xFF22C55E) : const Color(0xFFF59E0B),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          ),
                          child: Text(_loading ? '加载...' : '下一题', style: const TextStyle(fontSize: 16)),
                        ),
                      ),
                      if (_records.length >= 3) ...[
                        const SizedBox(height: 8),
                        SizedBox(
                          width: double.infinity,
                          height: 48,
                          child: OutlinedButton(
                            onPressed: _finishDiagnose,
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.grey,
                              side: const BorderSide(color: Color(0x40334455)),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            ),
                            child: const Text('完成诊断', style: TextStyle(fontSize: 15)),
                          ),
                        ),
                      ],
                    ],
                  )
                : SizedBox(
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
                  ),
          ),
        ),
      ],
    );
  }

  bool get _feedbackIsActive => _feedback != null;
}
