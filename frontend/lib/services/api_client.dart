import 'dart:convert';
import 'package:http/http.dart' as http;
import '../utils/constants.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  static String? _token;
  static void setToken(String? t) => _token = t;

  Future<Map<String, dynamic>> _request(String method, String path, {Map<String, dynamic>? body, Map<String, dynamic>? params}) async {
    final uri = Uri.parse('${AppConstants.baseUrl}$path').replace(queryParameters: params?.map((k, v) => MapEntry(k, v.toString())));
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (_token != null) headers['Authorization'] = 'Bearer $_token';
    final http.Response r;
    if (method == 'GET') {
      r = await http.get(uri, headers: headers);
    } else {
      r = await http.post(uri, headers: headers, body: body != null ? jsonEncode(body) : null);
    }
    final data = jsonDecode(r.body) as Map<String, dynamic>;
    if (r.statusCode >= 400 && data.containsKey('error')) throw Exception(data['error']);
    return data;
  }

  Future<Map<String, dynamic>> get(String path, {Map<String, dynamic>? params}) => _request('GET', path, params: params);
  Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? body}) => _request('POST', path, body: body);
}
