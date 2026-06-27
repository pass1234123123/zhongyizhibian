// 后端 - 上传记录模型
<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Upload extends Model
{
    protected  = [
        'user_id', 'raw_type', 'raw_content', 'raw_file_paths',
        'ai_result', 'reviewed_title', 'reviewed_disease_id',
        'reviewed_type_ids', 'reviewed_preview', 'reviewed_full_content',
        'reviewed_formulas', 'reviewed_acupuncture',
        'status', 'reject_reason', 'reviewer_id', 'reviewed_at'
    ];

    protected  = [
        'raw_file_paths' => 'array',
        'ai_result' => 'array',
        'reviewed_type_ids' => 'array',
        'reviewed_formulas' => 'array',
        'reviewed_acupuncture' => 'array'
    ];

    const STATUS_PROCESSING = 'processing';
    const STATUS_PENDING = 'pending';
    const STATUS_APPROVED = 'approved';
    const STATUS_REJECTED = 'rejected';
}
