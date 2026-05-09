import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const MathStarApp());
}

class MathStarApp extends StatelessWidget {
  const MathStarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '数学启明星',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFF59E0B),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
