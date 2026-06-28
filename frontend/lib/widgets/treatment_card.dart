import 'package:flutter/material.dart';
import '../utils/constants.dart';

class TreatmentCard extends StatelessWidget {
  final Map<String, dynamic> treatment;
  final VoidCallback onTap;
  const TreatmentCard({required this.treatment, required this.onTap});

  String _stars(double r) {
    String s = '';
    for (int i = 1; i <= 5; i++) s += i <= r.round() ? '\u2605' : '\u2606';
    return s;
  }

  @override
  Widget build(BuildContext context) {
    final types = List<String>.from(treatment['types'] ?? []);
    final isSpecial = treatment['is_special'] == true;
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Expanded(child: Text(treatment['title'] ?? '', style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600))),
              Text('\u00a5${treatment['price']}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(AppConstants.primaryColor))),
            ]),
            const SizedBox(height: 6),
            Wrap(gap: 4, children: [
              ...types.map((t) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(color: const Color(AppConstants.primaryLight), borderRadius: BorderRadius.circular(10)),
                child: Text(t, style: const TextStyle(fontSize: 10, color: Color(AppConstants.primaryColor)))),
              ),
              if (isSpecial)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(10)),
                  child: const Text('\u63a8\u8350', style: TextStyle(fontSize: 10, color: Colors.green)),
                ),
            ]),
            const SizedBox(height: 6),
            Row(children: [
              Text('$_stars((treatment['rating'] ?? 0).toDouble()) ${treatment['rating']}',
                style: const TextStyle(fontSize: 11, color: Color(AppConstants.starColor))),
              const SizedBox(width: 12),
              Text('\u53cd\u9988 ${treatment['feedback_count'] ?? 0}', style: const TextStyle(fontSize: 11, color: Color(AppConstants.textMuted))),
              const SizedBox(width: 12),
              Text('\u6709\u6548 ${treatment['effective_rate'] ?? 0}%', style: const TextStyle(fontSize: 11, color: Color(AppConstants.success))),
            ]),
          ]),
        ),
      ),
    );
  }
}
