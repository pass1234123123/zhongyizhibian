import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'pages/home/home_page.dart';
import 'pages/auth/login_page.dart';
import 'pages/auth/register_page.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: const ZhongYiZhiBanApp(),
    ),
  );
}

class ZhongYiZhiBanApp extends StatelessWidget {
  const ZhongYiZhiBanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '中医智伴',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF8B3A3A),
          primary: const Color(0xFF8B3A3A),
        ),
        fontFamily: 'PingFang SC',
        useMaterial3: true,
      ),
      home: const MainScaffold(),
    );
  }
}
