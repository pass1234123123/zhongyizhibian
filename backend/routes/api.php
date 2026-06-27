<?php
// 后端 API 路由

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\DiseaseController;
use App\Http\Controllers\Api\TreatmentController;
use App\Http\Controllers\Api\UploadController;
use App\Http\Controllers\Api\FeedbackController;
use App\Http\Controllers\Api\PurchaseController;
use App\Http\Controllers\Api\PointsController;
use App\Http\Controllers\Api\ShareController;
use App\Http\Controllers\Api\EarningController;
use App\Http\Controllers\Api\AdminController;

// ===== 公开接口 =====
Route::post('/auth/register', [AuthController::class, 'register']);
Route::post('/auth/login', [AuthController::class, 'login']);

Route::get('/disease-categories', [DiseaseController::class, 'categories']);
Route::get('/diseases', [DiseaseController::class, 'index']);
Route::get('/diseases/{id}', [DiseaseController::class, 'show']);
Route::get('/treatments/{id}', [TreatmentController::class, 'show']);
Route::get('/treatment-types', [TreatmentController::class, 'types']);

// ===== 需要登录 =====
Route::middleware('auth:sanctum')->group(function () {
    // 用户
    Route::get('/user/profile', [AuthController::class, 'profile']);
    Route::put('/user/profile', [AuthController::class, 'updateProfile']);

    // 上传
    Route::post('/uploads', [UploadController::class, 'store']);
    Route::get('/uploads/status/{id}', [UploadController::class, 'status']);
    Route::get('/uploads/my', [UploadController::class, 'myUploads']);

    // 购买
    Route::post('/purchases', [PurchaseController::class, 'store']);
    Route::get('/purchases/my', [PurchaseController::class, 'myPurchases']);
    Route::get('/treatments/{id}/purchased', [PurchaseController::class, 'check']);

    // 反馈
    Route::post('/feedbacks', [FeedbackController::class, 'store']);
    Route::get('/feedbacks/my', [FeedbackController::class, 'myFeedbacks']);

    // 积分
    Route::get('/points/log', [PointsController::class, 'log']);
    Route::get('/exchange-rules', [PointsController::class, 'rules']);
    Route::post('/exchanges', [PointsController::class, 'exchange']);

    // 分享
    Route::post('/shares', [ShareController::class, 'store']);
    Route::get('/shares/my', [ShareController::class, 'myShares']);

    // 收益
    Route::get('/earnings/summary', [EarningController::class, 'summary']);
    Route::get('/earnings/details', [EarningController::class, 'details']);
    Route::post('/withdrawals', [EarningController::class, 'withdraw']);
});

// ===== 管理员 =====
Route::middleware(['auth:sanctum', 'role:admin'])->prefix('admin')->group(function () {
    Route::get('/pending-uploads', [AdminController::class, 'pendingUploads']);
    Route::get('/pending-uploads/{id}', [AdminController::class, 'uploadDetail']);
    Route::post('/approve/{id}', [AdminController::class, 'approve']);
    Route::post('/reject/{id}', [AdminController::class, 'reject']);
});
