import 'package:flutter/material.dart';
import '../../services/treatment_service.dart';
import '../../utils/constants.dart';
import '../../widgets/treatment_card.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _service = TreatmentService();
  List<dynamic> _categories = [];
  List<dynamic> _treatments = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final cats = await _service.getCategories();
      final treats = await _service.getTreatments();
      if (mounted) setState(() { _categories = cats; _treatments = treats; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text(AppConstants.appName, style: TextStyle(fontWeight: FontWeight.w700)),
        centerTitle: true, backgroundColor: const Color(AppConstants.primaryColor), foregroundColor: Colors.white),
      body: _loading
        ? const Center(child: CircularProgressIndicator())
        : RefreshIndicator(
            onRefresh: _loadData,
            child: ListView(children: [
              Padding(padding: const EdgeInsets.all(16), child:
                TextField(decoration: InputDecoration(
                  hintText: '\u641c\u7d22\u75be\u75c5\uff0c\u5982\u80c3\u75db\u3001\u7cd6\u5c3f\u75c5...',
                  prefixIcon: const Icon(Icons.search), filled: true,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                ))),
              Padding(padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(children: [
                  const Text('\u75be\u75c5\u5206\u7c7b', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                  const Spacer(),
                  Text('\u5171${_categories.length}\u79d1', style: const TextStyle(fontSize: 12, color: Color(AppConstants.textMuted))),
                ])),
              if (_categories.isNotEmpty)
                SizedBox(
                  height: 90,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 12),
                    itemCount: _categories.length,
                    itemBuilder: (context, i) {
                      final c = _categories[i];
                      return GestureDetector(
                        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) =>
                          DiseaseListPage(categoryId: c['id'] ?? 0))),
                        child: Container(
                          width: 72, margin: const EdgeInsets.symmetric(horizontal: 4),
                          child: Column(children: [
                            Container(
                              width: 44, height: 44,
                              decoration: BoxDecoration(color: Color(int.parse((c['color'] ?? '#FEE4E2').replaceAll('#', '0xFF'))), borderRadius: BorderRadius.circular(22)),
                              child: Center(child: Text(c['icon'] ?? '', style: const TextStyle(fontSize: 20)))),
                            const SizedBox(height: 4),
                            Text(c['name'] ?? '', style: const TextStyle(fontSize: 11), textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
                          ]),
                        ),
                      );
                    },
                  ),
                ),
              Padding(padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(children: [
                  const Text('\u70ed\u95e8\u63a8\u8350', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                  const Spacer(),
                  TextButton(onPressed: () {}, child: const Text('\u67e5\u770b\u66f4\u591a', style: TextStyle(fontSize: 12))),
                ])),
              ..._treatments.take(6).map((t) => TreatmentCard(
                treatment: t,
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => TreatmentDetailPage(id: t['id'] ?? 0))),
              )),
              const SizedBox(height: 80),
            ]),
          ),
    );
  }
}

// Forward declarations for pages referenced by routes
class DiseaseListPage extends StatelessWidget {
  final int categoryId;
  const DiseaseListPage({required this.categoryId, super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u75be\u75c5\u5217\u8868')), body: const Center(child: Text('\u52a0\u8f7d\u4e2d...')));
}

class TreatmentDetailPage extends StatelessWidget {
  final int id;
  const TreatmentDetailPage({required this.id, super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u6cbb\u7597\u65b9\u6848')), body: const Center(child: Text('\u52a0\u8f7d\u4e2d...')));
}

class UploadPage extends StatelessWidget {
  const UploadPage({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u4e0a\u4f20')), body: const Center(child: Text('\u52a0\u8f7d\u4e2d...')));
}

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u4e2a\u4eba')), body: const Center(child: Text('\u52a0\u8f7d\u4e2d...')));
}

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u767b\u5f55')), body: const Center(child: Text('\u767b\u5f55\u9875')));
}

class RegisterPage extends StatelessWidget {
  const RegisterPage({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u6ce8\u518c')), body: const Center(child: Text('\u6ce8\u518c\u9875')));
}

class MemberCenterPage extends StatelessWidget {
  const MemberCenterPage({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u4f1a\u5458\u4e2d\u5fc3')), body: const Center(child: Text('\u4f1a\u5458\u4e2d\u5fc3')));
}

class AdminPage extends StatelessWidget {
  const AdminPage({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('\u7ba1\u7406\u540e\u53f0')), body: const Center(child: Text('\u7ba1\u7406\u540e\u53f0')));
}
