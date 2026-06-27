// 后端 - 疾病模型
<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Disease extends Model
{
    protected  = [
        'name', 'pinyin', 'category_id', 'keywords',
        'description', 'icon', 'sort_order', 'status'
    ];

    protected  = [
        'keywords' => 'array'
    ];

    public function treatments()
    {
        return ->hasMany(Treatment::class);
    }

    public function category()
    {
        return ->belongsTo(DiseaseCategory::class, 'category_id');
    }
}
