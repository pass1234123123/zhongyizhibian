import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  User? _user;
  bool _loading = false;
  bool _initialized = false;

  User? get user => _user;
  bool get loading => _loading;
  bool get isLoggedIn => _user != null;
  bool get isAdmin => _user?.role == 'admin';
  bool get initialized => _initialized;

  Future<void> init() async {
    final token = await AuthService.getSavedToken();
    if (token != null) {
      try {
        final user = await _authService.getProfile();
        _user = user;
      } catch (_) {
        await _authService.logout();
      }
    }
    _initialized = true;
    notifyListeners();
  }

  Future<String?> login(String phone, String password) async {
    _loading = true;
    notifyListeners();
    try {
      final r = await _authService.login(phone, password);
      _user = User.fromJson(r['user']);
      return null;
    } catch (e) {
      return e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<String?> register(String phone, String password, String username) async {
    _loading = true;
    notifyListeners();
    try {
      final r = await _authService.register(phone, password, username);
      _user = User.fromJson(r['user']);
      return null;
    } catch (e) {
      return e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _user = null;
    notifyListeners();
  }
}
