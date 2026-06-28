class Treatment {
  final int id;
  final String title;
  final double price;
  final double rating;
  final int feedbackCount;
  final int effectiveRate;
  final String preview;
  final String? fullContent;
  final List<String> types;
  final bool isSpecial;
  final bool canView;
  final String? viewMsg;
  final bool isMember;
  final bool isFavorited;
  final List<Formula> formulas;
  final List<Acupoint> acupoints;

  Treatment({
    required this.id, required this.title, this.price = 0, this.rating = 0,
    this.feedbackCount = 0, this.effectiveRate = 0, this.preview = '',
    this.fullContent, this.types = const [], this.isSpecial = false,
    this.canView = false, this.viewMsg, this.isMember = false,
    this.isFavorited = false, this.formulas = const [], this.acupoints = const [],
  });
  factory Treatment.fromJson(Map<String, dynamic> j) => Treatment(
    id: j['id'] ?? 0, title: j['title'] ?? '',
    price: (j['price'] ?? 0).toDouble(), rating: (j['rating'] ?? 0).toDouble(),
    feedbackCount: j['feedback_count'] ?? 0,
    effectiveRate: j['effective_rate'] ?? 0, preview: j['preview'] ?? '',
    fullContent: j['full_content'],
    types: List<String>.from(j['types'] ?? []),
    isSpecial: j['is_special'] == true, canView: j['can_view'] == true,
    viewMsg: j['view_msg'], isMember: j['is_member'] == true,
    isFavorited: j['is_favorited'] == true,
    formulas: (j['formulas'] as List?)?.map((e) => Formula.fromJson(e)).toList() ?? [],
    acupoints: (j['acupoints'] as List?)?.map((e) => Acupoint.fromJson(e)).toList() ?? []);
}

class Formula {
  final String formulaName;
  final String ingredients;
  final String usageText;
  final String note;
  Formula({this.formulaName = '', this.ingredients = '', this.usageText = '', this.note = ''});
  factory Formula.fromJson(Map<String, dynamic> j) => Formula(
    formulaName: j['formula_name'] ?? '', ingredients: j['ingredients'] ?? '',
    usageText: j['usage_text'] ?? '', note: j['note'] ?? '');
}

class Acupoint {
  final String points;
  final String method;
  final String course;
  Acupoint({this.points = '', this.method = '', this.course = ''});
  factory Acupoint.fromJson(Map<String, dynamic> j) => Acupoint(
    points: j['points'] ?? '', method: j['method'] ?? '', course: j['course'] ?? '');
}
