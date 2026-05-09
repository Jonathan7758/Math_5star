import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:http/http.dart' as http;
import '../api/api_client.dart';
import '../api/api_config.dart';
import 'dart:io';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _api = ApiClient();
  final _serverController = TextEditingController();
  Map<String, dynamic>? _versionInfo;
  String? _updateMsg;
  int _studentId = ApiConfig.studentId;
  bool _checkingUpdate = false;
  bool _downloading = false;
  double _downloadProgress = 0;

  // App version
  static const _currentVersion = '1.0.1';
  static const _currentVersionCode = 2;

  @override
  void initState() {
    super.initState();
    _serverController.text = ApiConfig.baseUrl;
    _checkVersion();
  }

  Future<void> _checkVersion() async {
    setState(() { _checkingUpdate = true; _updateMsg = null; });
    try {
      final v = await _api.get('/api/health/version');
      final serverCode = v['version_code'] ?? 0;
      if (serverCode > _currentVersionCode) {
        setState(() => _updateMsg = '\u{1F4E6} \u{65B0}\u{7248}\u{672C} v${v['version']} \u{53EF}\u{7528}');
        _versionInfo = v;
      } else {
        setState(() => _updateMsg = '\u{2714} \u{5DF2}\u{662F}\u{6700}\u{65B0}\u{7248}\u{672C}');
        _versionInfo = v;
      }
    } catch (_) {
      setState(() => _updateMsg = '\u{26A0} \u{65E0}\u{6CD5}\u{8FDE}\u{63A5}\u{670D}\u{52A1}\u{5668}');
    }
    setState(() => _checkingUpdate = false);
  }

  Future<void> _downloadAndInstall() async {
    if (_versionInfo == null) return;
    final apkUrl = '${ApiConfig.baseUrl}${_versionInfo!['apk_url'] ?? '/flutter/app-release.apk'}';

    setState(() { _downloading = true; _downloadProgress = 0; });

    try {
      final tempDir = Directory.systemTemp;
      final file = File('${tempDir.path}/math_5star_update.apk');

      final response = await http.get(Uri.parse(apkUrl));
      if (response.statusCode == 200) {
        await file.writeAsBytes(response.bodyBytes);
        setState(() { _downloading = false; _updateMsg = '\u{2705} \u{4E0B}\u{8F7D}\u{5B8C}\u{6210}'; });

        // Trigger install via platform intent
        // On Android, this opens the installer
        try {
          final result = await Process.run('cmd', ['/c', 'start', file.path]);
          setState(() => _updateMsg = '\u{1F4F2} \u{8BF7}\u{5728}\u{5F39}\u{7A97}\u{4E2D}\u{5B89}\u{88C5}\u{66F4}\u{65B0}');
        } catch (_) {
          setState(() => _updateMsg = '\u{1F4C2} APK\u{5DF2}\u{4FDD}\u{5B58}\u{5230}: ${file.path}');
        }
      } else {
        setState(() { _downloading = false; _updateMsg = '\u{274C} \u{4E0B}\u{8F7D}\u{5931}\u{8D25} (${response.statusCode})'; });
      }
    } catch (e) {
      setState(() { _downloading = false; _updateMsg = '\u{274C} \u{4E0B}\u{8F7D}\u{5931}\u{8D25}'; });
    }
  }

  Future<void> _saveServer() async {
    final url = _serverController.text.trim();
    if (url.isNotEmpty && url != ApiConfig.baseUrl) {
      ApiConfig.baseUrl = url;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('\u{2705} \u{670D}\u{52A1}\u{5668}\u{5730}\u{5740}\u{5DF2}\u{66F4}\u{65B0}'), duration: Duration(seconds: 2)));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasUpdate = _versionInfo != null && (_versionInfo!['version_code'] ?? 0) > _currentVersionCode;
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(backgroundColor: Colors.transparent, title: const Text('\u{8BBE}\u{7F6E}')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // Version + Update card
          Container(
            width: double.infinity, padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: hasUpdate ? const Color(0x3022C55E) : const Color(0x201E293B),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: hasUpdate ? const Color(0x4022C55E) : const Color(0x30334455)),
            ),
            child: Column(children: [
              const Text('\u{6570}\u{5B66}\u{542F}\u{660E}\u{661F}', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              Text('v$_currentVersion (build $_currentVersionCode)', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
              const SizedBox(height: 14),
              if (_checkingUpdate)
                const Row(mainAxisAlignment: MainAxisAlignment.center, children: [SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFFBBF24))), SizedBox(width: 8), Text('\u{68C0}\u{67E5}\u{66F4}\u{65B0}\u{4E2D}...', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12))])
              else if (_updateMsg != null)
                Text(_updateMsg!, style: TextStyle(color: hasUpdate ? const Color(0xFF4ADE80) : const Color(0xFF94A3B8), fontSize: 13, fontWeight: hasUpdate ? FontWeight.bold : FontWeight.normal)),
              if (hasUpdate) ...[
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _downloading ? null : _downloadAndInstall,
                    icon: _downloading ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.download, size: 18),
                    label: Text(_downloading ? '\u{4E0B}\u{8F7D}\u{4E2D}...' : '\u{7ACB}\u{5373}\u{5347}\u{7EA7}'),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF22C55E), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 12), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                  ),
                ),
                if (_versionInfo?['release_notes'] != null) ...[
                  const SizedBox(height: 8),
                  Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: const Color(0x101E293B), borderRadius: BorderRadius.circular(10)), child: Text('\u{66F4}\u{65B0}\u{5185}\u{5BB9}: ${_versionInfo!['release_notes']}', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12))),
                ],
              ],
            ]),
          ).animate().fadeIn(duration: 300.ms),

          const SizedBox(height: 14),

          // Check update button
          SizedBox(width: double.infinity, child: OutlinedButton.icon(onPressed: _checkVersion, icon: const Icon(Icons.refresh, size: 18), label: const Text('\u{68C0}\u{67E5}\u{66F4}\u{65B0}'), style: OutlinedButton.styleFrom(foregroundColor: const Color(0xFFFBBF24), side: const BorderSide(color: Color(0x30FBBF24)), padding: const EdgeInsets.symmetric(vertical: 12), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))))).animate().fadeIn(delay: 100.ms),

          const SizedBox(height: 24),

          // Server config
          const Text('\u{670D}\u{52A1}\u{5668}\u{914D}\u{7F6E}', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          TextField(
            controller: _serverController,
            style: const TextStyle(color: Colors.white, fontSize: 14),
            decoration: InputDecoration(
              hintText: 'http://101.96.217.150',
              hintStyle: TextStyle(color: Colors.grey[600]),
              suffixIcon: IconButton(icon: const Icon(Icons.save, size: 18), onPressed: _saveServer),
              filled: true, fillColor: const Color(0x101E293B),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0x30334455))),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0x30334455))),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFF59E0B))),
            ),
          ).animate().fadeIn(delay: 200.ms),

          const SizedBox(height: 24),

          // Student profile
          const Text('\u{5B66}\u{751F}\u{6863}\u{6848}', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Row(children: List.generate(3, (i) {
            final id = i + 1; final isActive = id == _studentId;
            return Expanded(child: Padding(padding: EdgeInsets.only(left: i > 0 ? 8.0 : 0), child: GestureDetector(
              onTap: () => setState(() { _studentId = id; ApiConfig.studentId = id; }),
              child: Container(padding: const EdgeInsets.symmetric(vertical: 14), decoration: BoxDecoration(color: isActive ? const Color(0x30F59E0B) : const Color(0x101E293B), borderRadius: BorderRadius.circular(12), border: Border.all(color: isActive ? const Color(0x80F59E0B) : const Color(0x20334455))),
                child: Column(children: [
                  Text('\u{1F393}', style: TextStyle(fontSize: 24, color: isActive ? const Color(0xFFFBBF24) : Colors.grey[600])),
                  const SizedBox(height: 4),
                  Text('\u{5B66}\u{751F} $id', style: TextStyle(color: isActive ? Colors.white : Colors.grey[600], fontSize: 13)),
                ]),
              ),
            )));
          })).animate().fadeIn(delay: 300.ms),

          const SizedBox(height: 32),
          Center(child: Text('\u{6BCF}\u{5929}10\u{5206}\u{949F} \u{B7} \u{70B9}\u{4EAE}\u{77E5}\u{8BC6}\u{7684}\u{661F}\u{7A7A}', style: TextStyle(color: Colors.grey[700], fontSize: 11))),
        ]),
      ),
    );
  }
}
