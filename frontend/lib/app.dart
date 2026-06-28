import 'package:flutter/material.dart';
import 'utils/constants.dart';
import 'pages/home/home_page.dart';
import 'pages/auth/login_page.dart';
import 'pages/auth/register_page.dart';
import 'pages/upload/upload_page.dart';
import 'pages/profile/profile_page.dart';
import 'pages/member/member_center_page.dart';
import 'pages/admin/admin_page.dart';
import 'pages/disease/disease_list_page.dart';

class ZhongYiApp extends StatelessWidget {
  const ZhongYiApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConstants.appName,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(AppConstants.primaryColor), primary: const Color(AppConstants.primaryColor)),
        useMaterial3: true, fontFamily: 'PingFang SC',
      ),
      home: const MainScaffold(),
      routes: {
        '/login': (context) => const LoginPage(),
        '/register': (context) => const RegisterPage(),
        '/profile': (context) => const ProfilePage(),
        '/member': (context) => const MemberCenterPage(),
        '/admin': (context) => const AdminPage(),
      },
    );
  }
}

class MainScaffold extends StatefulWidget {
  const MainScaffold({super.key});
  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int _currentIndex = 0;
  final _pages = [const HomePage(), const DiseaseListPage(categoryId: 1), const UploadPage(), const ProfilePage()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) => setState(() => _currentIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: '\u9996\u9875'),
          NavigationDestination(icon: Icon(Icons.search_outlined), selectedIcon: Icon(Icons.search), label: '\u75be\u75c5'),
          NavigationDestination(icon: Icon(Icons.upload_outlined), selectedIcon: Icon(Icons.upload), label: '\u4e0a\u4f20'),
          NavigationDestination(icon: Icon(Icons.person_outlined), selectedIcon: Icon(Icons.person), label: '\u6211\u7684'),
        ],
      ),
    );
  }
}
