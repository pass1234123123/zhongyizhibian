import '../models/treatment.dart';
import '../models/feedback.dart';
import 'api_client.dart';

class TreatmentService {
  final _api = ApiClient();

  Future<List<dynamic>> getCategories() async {
    final r = await _api.get('/api/categories');
    return r['list'] ?? [];
  }

  Future<List<dynamic>> getDiseases({int? categoryId}) async {
    final params = <String, dynamic>{};
    if (categoryId != null) params['category_id'] = categoryId;
    final r = await _api.get('/api/diseases', params: params);
    return r['list'] ?? [];
  }

  Future<List<dynamic>> getTreatments({int? diseaseId, String? search}) async {
    final params = <String, dynamic>{};
    if (diseaseId != null) params['disease_id'] = diseaseId;
    if (search != null) params['search'] = search;
    final r = await _api.get('/api/treatments', params: params);
    return r['list'] ?? [];
  }

  Future<Treatment> getTreatmentDetail(int id) async {
    final r = await _api.get('/api/treatments/$id');
    return Treatment.fromJson(r);
  }

  Future<Map<String, dynamic>> toggleFavorite(int treatmentId) async {
    return await _api.post('/api/favorites/toggle', body: {'treatment_id': treatmentId});
  }

  Future<List<dynamic>> getFavorites() async {
    final r = await _api.get('/api/favorites');
    return r['list'] ?? [];
  }

  Future<String> submitFeedback(int tid, int rating, String efficacy, String desc, int days) async {
    final r = await _api.post('/api/feedback', body: {
      'treatment_id': tid, 'rating': rating, 'efficacy': efficacy,
      'description': desc, 'course_days': days});
    return r['message'] as String;
  }

  Future<FeedbackSummary> getFeedback(int tid) async {
    final r = await _api.get('/api/feedback/$tid');
    return FeedbackSummary.fromJson(r);
  }
}
