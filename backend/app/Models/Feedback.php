// 后端 - 疗效反馈模型
<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Feedback extends Model
{
    protected  = [
        'treatment_id', 'user_id', 'rating', 'effectiveness',
        'content', 'course_days', 'images', 'points_awarded',
        'is_recommended', 'status'
    ];

    protected  = [
        'images' => 'array'
    ];

    public function treatment()
    {
        return ->belongsTo(Treatment::class);
    }

    public function user()
    {
        return ->belongsTo(User::class);
    }
}
