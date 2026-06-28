import 'api_client.dart';

class MemberService {
  final _api = ApiClient();

  Future<Map<String, dynamic>> getStatus() async {
    return await _api.get('/api/member/status');
  }

  Future<String> upgrade() async {
    final r = await _api.post('/api/member/apply', body: {'action': 'upgrade'});
    return r['message'] as String;
  }

  Future<String> applyContributor() async {
    final r = await _api.post('/api/member/apply', body: {'action': 'renewal'});
    return r['message'] as String;
  }

  Future<Map<String, dynamic>> getAdminSettings() async {
    return await _api.get('/api/admin/member/settings');
  }

  Future<void> saveAdminSettings(double fee, int days) async {
    await _api.post('/api/admin/member/settings', body: {'annual_fee': fee, 'free_duration_days': days});
  }

  Future<List<dynamic>> getMemberList() async {
    final r = await _api.get('/api/admin/member/list');
    return r['list'] ?? [];
  }

  Future<List<dynamic>> getApplications() async {
    final r = await _api.get('/api/admin/member/applications');
    return r['list'] ?? [];
  }

  Future<void> approveApplication(int id) async {
    await _api.post('/api/admin/member/applications', body: {'application_id': id, 'action': 'approve'});
  }

  Future<void> rejectApplication(int id, String reason) async {
    await _api.post('/api/admin/member/applications', body: {'application_id': id, 'action': 'reject', 'review_note': reason});
  }
}
