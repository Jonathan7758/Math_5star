import 'dart:typed_data';
import 'dart:math';
import 'dart:async';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/services.dart';

/// WAV audio synthesizer with actual playback via audioplayers.
/// Generates tones in memory — no external audio files needed.
class GameSound {
  static final _player = AudioPlayer();
  static bool _enabled = true;
  static const _sampleRate = 22050;
  static bool _playing = false;

  static void toggle() => _enabled = !_enabled;
  static bool get isEnabled => _enabled;

  static Future<void> correct() async {
    if (!_enabled) return;
    HapticFeedback.lightImpact();
    final bytes = _gen([523, 659, 784], [0.08, 0.08, 0.15], 0.3, 'triangle');
    await _play(bytes);
  }

  static Future<void> incorrect() async {
    if (!_enabled) return;
    HapticFeedback.heavyImpact();
    final bytes = _gen([200], [0.25], 0.2, 'square');
    await _play(bytes);
  }

  static Future<void> combo() async {
    if (!_enabled) return;
    final bytes = _gen([784, 988, 1175], [0.06, 0.06, 0.12], 0.3, 'sine');
    await _play(bytes);
  }

  static Future<void> achievement() async {
    if (!_enabled) return;
    final bytes = _gen([523, 659, 784, 1047], [0.1, 0.1, 0.1, 0.3], 0.35, 'sine');
    await _play(bytes);
  }

  static Future<void> levelUp() async {
    if (!_enabled) return;
    final bytes = _gen([392, 523, 659, 784, 1047], [0.08, 0.08, 0.08, 0.08, 0.2], 0.35, 'sine');
    await _play(bytes);
  }

  static Future<void> click() async {
    if (!_enabled) return;
    final bytes = _gen([800], [0.04], 0.15, 'sine');
    await _play(bytes);
  }

  static Uint8List _gen(List<int> freqs, List<double> durations, double vol, String type) {
    int total = 0; for (var d in durations) total += (d * _sampleRate).toInt();
    final data = Int16List(total + 200);
    int off = 0;
    for (int i = 0; i < freqs.length; i++) {
      final f = freqs[i], n = (durations[i] * _sampleRate).toInt();
      for (int s = 0; s < n; s++) {
        double v;
        switch (type) {
          case 'square': v = sin(2 * pi * f * s / _sampleRate) > 0 ? 1.0 : -1.0; break;
          case 'triangle': v = 2 * (2 * (f * s / _sampleRate - (f * s / _sampleRate).floor()) - 1).abs() - 1; break;
          default: v = sin(2 * pi * f * s / _sampleRate);
        }
        double env = s < 30 ? s / 30.0 : s > n - 150 ? (n - s) / 150.0 : 1.0;
        data[off + s] = (v * vol * env * 32767).toInt().clamp(-32768, 32767);
      }
      off += n;
    }
    final ds = data.length * 2;
    final w = BytesBuilder();
    w.add('RIFF'.codeUnits); w.add(_i32(36 + ds)); w.add('WAVE'.codeUnits);
    w.add('fmt '.codeUnits); w.add(_i32(16)); w.add(_i16(1)); w.add(_i16(1));
    w.add(_i32(_sampleRate)); w.add(_i32(_sampleRate * 2)); w.add(_i16(2)); w.add(_i16(16));
    w.add('data'.codeUnits); w.add(_i32(ds)); w.add(data.buffer.asUint8List());
    return w.toBytes();
  }

  static Uint8List _i32(int v) => Uint8List(4)..buffer.asByteData().setInt32(0, v, Endian.little);
  static Uint8List _i16(int v) => Uint8List(2)..buffer.asByteData().setInt16(0, v, Endian.little);

  static Future<void> _play(Uint8List wav) async {
    if (_playing) return;
    _playing = true;
    try {
      await _player.stop();
      await _player.play(BytesSource(wav));
    } catch (_) {
      HapticFeedback.lightImpact();
    }
    _playing = false;
  }
}
