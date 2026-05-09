import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_config.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._();
  factory ApiClient() => _instance;
  ApiClient._();

  final _client = http.Client();

  Future<Map<String, dynamic>> get(String path, {Map<String, String>? headers}) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$path');
    final response = await _client.get(uri, headers: headers);
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body, {Map<String, String>? headers}) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$path');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json', ...?headers},
      body: jsonEncode(body),
    );
    return jsonDecode(response.body);
  }

  // --- Game API methods ---

  Future<Map<String, dynamic>> getNextQuestion({String? kpId}) {
    final params = 'student_id=${ApiConfig.studentId}${kpId != null ? '&kp_id=$kpId' : ''}';
    return get('/api/exercise/next?$params');
  }

  Future<Map<String, dynamic>> submitAnswer({
    required String questionId,
    required String answer,
    int hintLevel = 0,
  }) {
    return post('/api/exercise/submit', {
      'student_id': ApiConfig.studentId,
      'question_id': questionId,
      'answer': answer,
      'hint_level_used': hintLevel,
    });
  }

  Future<Map<String, dynamic>> processReward(bool isCorrect, int combo) {
    return post('/api/rewards/process?student_id=${ApiConfig.studentId}&is_correct=$isCorrect&combo=$combo', {});
  }

  Future<Map<String, dynamic>> getRewardsStatus() {
    return get('/api/rewards/status?student_id=${ApiConfig.studentId}');
  }

  Future<Map<String, dynamic>> submitDiagnose(List<Map<String, dynamic>> records) {
    return post('/api/diagnose', {
      'student_id': ApiConfig.studentId,
      'records': records,
    });
  }

  Future<Map<String, dynamic>> getParentDashboard(String pin) {
    return get(
      '/api/parent/dashboard?student_id=${ApiConfig.studentId}',
      headers: {'x-parent-pin': pin},
    );
  }
}
