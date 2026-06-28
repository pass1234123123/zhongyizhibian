import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import 'api_client.dart';

class AuthService {
  final _api = ApiClient();

  Future<Map<String, dynamic>> login(String phone, String password) async {
    final r = await _api.post('/api/auth/login', body: {'phone': phone, 'password': password});
    final token = r['token'] as String;
    ApiClient.setToken(token);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
    await prefs.setString('user', jsonEncode(r['user']));
    return r;
  }

  Future<Map<String, dynamic>> register(String phone, String password, String username) async {
    final r = await _api.post('/api/auth/register', body: {'phone': phone, 'password': password, 'username': username});
    final token = r['token'] as String;
    ApiClient.setToken(token);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
    await prefs.setString('user', jsonEncode(r['user']));
    return r;
  }

  Future<void> logout() async {
    ApiClient.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user');
  }

  Future<User> getProfile() async {
    final r = await _api.get('/api/auth/me');
    return User.fromJson(r);
  }

  static Future<String?> getSavedToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }
}
