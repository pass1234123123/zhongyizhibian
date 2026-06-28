class Category {
  final int id;
  final String name;
  final String icon;
  final String color;
  final int diseaseCount;
  Category({required this.id, required this.name, this.icon = '',
    this.color = '#FEE4E2', this.diseaseCount = 0});
  factory Category.fromJson(Map<String, dynamic> j) => Category(
    id: j['id'] ?? 0, name: j['name'] ?? '',
    icon: j['icon'] ?? '', color: j['color'] ?? '#FEE4E2',
    diseaseCount: j['disease_count'] ?? 0);
}

class Disease {
  final int id;
  final int categoryId;
  final String name;
  final String icon;
  final int treatmentCount;
  Disease({required this.id, this.categoryId = 0, required this.name,
    this.icon = '', this.treatmentCount = 0});
  factory Disease.fromJson(Map<String, dynamic> j) => Disease(
    id: j['id'] ?? 0, categoryId: j['category_id'] ?? 0, name: j['name'] ?? '',
    icon: j['icon'] ?? '', treatmentCount: j['treatment_count'] ?? 0);
}
