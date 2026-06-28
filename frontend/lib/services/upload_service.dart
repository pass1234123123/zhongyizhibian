import 'api_client.dart';

class UploadService {
  final _api = ApiClient();

  Future<Map<String, dynamic>> uploadContent(String content) async {
    return await _api.post('/api/upload', body: {'content': content});
  }

  Future<List<dynamic>> getUploads() async {
    final r = await _api.get('/api/uploads');
    return r['list'] ?? [];
  }
}
