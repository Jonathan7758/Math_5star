import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../api/api_client.dart';

class ParentScreen extends StatefulWidget {
  const ParentScreen({super.key});

  @override
  State<ParentScreen> createState() => _ParentScreenState();
}

class _ParentScreenState extends State<ParentScreen> {
  final _api = ApiClient();
  final _pinController = TextEditingController();
  bool _authenticated = false;
  bool _loading = false;
  Map<String, dynamic>? _dashboard;
  String? _error;

  Future<void> _login() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await _api.getParentDashboard(_pinController.text);
      setState(() { _dashboard = data; _authenticated = true; _loading = false; });
    } catch (e) {
      setState(() { _error = 'PIN码错误'; _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_authenticated) {
      return Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('🔐', style: TextStyle(fontSize: 48)),
                const SizedBox(height: 16),
                const Text('家长看板', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                const SizedBox(height: 24),
                TextField(
                  controller: _pinController,
                  obscureText: true,
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  style: const TextStyle(color: Colors.white, fontSize: 24, letterSpacing: 8),
                  textAlign: TextAlign.center,
                  decoration: InputDecoration(
                    hintText: 'PIN码',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    counterText: '',
                  ),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 8),
                  Text(_error!, style: const TextStyle(color: Color(0xFFEF4444), fontSize: 13)),
                ],
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _login,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF059669),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    child: Text(_loading ? '验证中...' : '进入看板', style: const TextStyle(fontSize: 16)),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final heatmap = (_dashboard?['mastery_heatmap'] as List?) ?? [];
    final mastered = heatmap.where((h) => (h['score'] ?? 0) >= 0.6).length;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('家长看板'),
        actions: [
          TextButton(onPressed: () => setState(() { _authenticated = false; _dashboard = null; }), child: const Text('退出', style: TextStyle(color: Colors.grey))),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Stats grid
            Row(
              children: [
                Expanded(child: _StatCard(value: '$mastered', label: '已掌握', color: const Color(0xFF2563EB))),
                const SizedBox(width: 12),
                Expanded(child: _StatCard(value: '${_dashboard?['streak_days'] ?? 0}', label: '连胜天', color: const Color(0xFFFBBF24))),
                const SizedBox(width: 12),
                Expanded(child: _StatCard(value: '${_dashboard?['total_xp'] ?? 0}', label: '总XP', color: const Color(0xFF22C55E))),
              ],
            ).animate().fadeIn(duration: 400.ms),

            const SizedBox(height: 24),

            // Heatmap
            const Text('掌握度热力图', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: heatmap.map<Widget>((h) {
                final score = (h['score'] ?? 0).toDouble();
                Color color;
                if (score >= 0.8) color = const Color(0xFF22C55E);
                else if (score >= 0.6) color = const Color(0xFF4ADE80);
                else if (score >= 0.4) color = const Color(0xFFFBBF24);
                else if (score > 0) color = const Color(0xFFF97316);
                else color = const Color(0xFF334155);

                return Tooltip(
                  message: '${h['kp_name']}: ${(score * 100).toInt()}%',
                  child: Container(
                    width: 56, height: 56,
                    decoration: BoxDecoration(
                      color: color.withAlpha(180),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    alignment: Alignment.center,
                    child: Text('${(score * 100).toInt()}%', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                );
              }).toList(),
            ),

            const SizedBox(height: 24),

            // Suggestions
            if ((_dashboard?['suggestions'] as List?)?.isNotEmpty == true) ...[
              const Text('建议', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              ...(_dashboard!['suggestions'] as List).map((s) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text('• $s', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
              )),
            ],
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String value;
  final String label;
  final Color color;
  const _StatCard({required this.value, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Column(
        children: [
          Text(value, style: TextStyle(color: color, fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(color: Colors.grey[500], fontSize: 12)),
        ],
      ),
    );
  }
}
