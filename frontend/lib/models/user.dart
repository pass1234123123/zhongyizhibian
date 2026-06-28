class User {
  final int id;
  final String phone;
  final String username;
  final String role;
  final int points;
  final double balance;
  User({required this.id, required this.phone, this.username = '',
    this.role = 'user', this.points = 0, this.balance = 0.0});

  factory User.fromJson(Map<String, dynamic> j) => User(
    id: j['id'] ?? 0, phone: j['phone'] ?? '',
    username: j['username'] ?? '', role: j['role'] ?? 'user',
    points: j['points'] ?? 0, balance: (j['balance'] ?? 0).toDouble());
  Map<String, dynamic> toJson() => {'id': id, 'phone': phone, 'username': username,
    'role': role, 'points': points, 'balance': balance};
}
