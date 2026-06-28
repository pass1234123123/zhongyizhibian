class FeedbackItem {
  final int id;
  final int rating;
  final String efficacy;
  final String description;
  final int courseDays;
  final String username;
  final String createdAt;
  FeedbackItem({required this.id, this.rating = 5, this.efficacy = '',
    this.description = '', this.courseDays = 0, this.username = '', this.createdAt = ''});
  factory FeedbackItem.fromJson(Map<String, dynamic> j) => FeedbackItem(
    id: j['id'] ?? 0, rating: j['rating'] ?? 5, efficacy: j['efficacy'] ?? '',
    description: j['description'] ?? '', courseDays: j['course_days'] ?? 0,
    username: j['username'] ?? '', createdAt: j['created_at'] ?? '');
}

class FeedbackSummary {
  final int total;
  final double avgRating;
  final Map<String, int> efficacyStats;
  final List<FeedbackItem> list;
  FeedbackSummary({this.total = 0, this.avgRating = 0,
    this.efficacyStats = const {}, this.list = const []});
  factory FeedbackSummary.fromJson(Map<String, dynamic> j) => FeedbackSummary(
    total: j['total'] ?? 0, avgRating: (j['avg_rating'] ?? 0).toDouble(),
    efficacyStats: Map<String, int>.from(j['efficacy_stats'] ?? {}),
    list: (j['list'] as List?)?.map((e) => FeedbackItem.fromJson(e)).toList() ?? []);
}
