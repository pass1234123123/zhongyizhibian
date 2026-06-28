import 'package:flutter/material.dart';
import '../services/member_service.dart';

class MemberProvider extends ChangeNotifier {
  final MemberService _service = MemberService();
  Map<String, dynamic> _status = {};
  bool _loading = false;

  Map<String, dynamic> get status => _status;
  bool get isMember => _status['is_member'] == true;
  int get approvedUploads => _status['approved_uploads'] ?? 0;

  Future<void> loadStatus() async {
    _status = await _service.getStatus();
    notifyListeners();
  }

  Future<String?> upgrade() async {
    try {
      final msg = await _service.upgrade();
      await loadStatus();
      return null;
    } catch (e) {
      return e.toString();
    }
  }

  Future<String?> applyContributor() async {
    try {
      final msg = await _service.applyContributor();
      return null;
    } catch (e) {
      return e.toString();
    }
  }
}
