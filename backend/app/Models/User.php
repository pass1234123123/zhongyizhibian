// 后端 - 用户模型
<?php
namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens;

    protected  = [
        'phone', 'username', 'password_hash', 'role',
        'avatar', 'balance', 'points', 'total_earnings'
    ];

    protected  = ['password_hash'];

    const ROLE_USER = 'user';
    const ROLE_REVIEWER = 'reviewer';
    const ROLE_ADMIN = 'admin';
}
