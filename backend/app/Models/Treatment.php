// 后端 - 治疗方案模型
<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Treatment extends Model
{
    protected  = [
        'upload_id', 'disease_id', 'type_ids', 'title',
        'preview_content', 'full_content', 'price',
        'avg_rating', 'effectiveness_rate', 'total_feedbacks',
        'share_count', 'purchase_count', 'uploader_id', 'status'
    ];

    protected  = [
        'type_ids' => 'array'
    ];

    public function disease()
    {
        return ->belongsTo(Disease::class);
    }

    public function uploader()
    {
        return ->belongsTo(User::class, 'uploader_id');
    }

    public function feedbacks()
    {
        return ->hasMany(Feedback::class);
    }

    public function purchases()
    {
        return ->hasMany(Purchase::class);
    }
}
