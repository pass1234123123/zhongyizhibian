# 中医智慧平台 (TCM Wisdom Platform)

> 中医治疗方案查询与分享平台

## 技术栈 (当前运行版)
- **后端**: Python Flask 3.x + SQLite + PyJWT
- **前端**: 单页 HTML + Vanilla JS (服务端渲染)
- **部署**: Gunicorn + systemd (Debian 12)
- **部署地址**: http://103.73.161.36:5000

## 项目结构

```
中医易经/
├── app.py              # Flask 后端 (25 个 API 端点)
├── models.py           # SQLite 数据模型 + 种子数据 (11 张表)
├── config.py           # JWT 配置、数据库路径
├── run.py              # 本地开发启动脚本
├── test_api.py         # API 集成测试 (25 用例)
├── templates/
│   ├── index.html      # 前端页面 (含全部 JS)
│   └── app.js          # (历史遗留, JS 已内联至 index.html)
├── static/             # 静态资源目录
├── uploads/            # 上传文件存储目录
├── demo.html / demo.js # 原始原型 (历史参考)
└── 产品开发文档.md       # 完整产品需求文档
```

## 管理员登录
- 手机: `13800000000`
- 密码: `admin123`
- 地址: http://103.73.161.36:5000

## 本地开发

```bash
cd '中医易经'
pip install flask flask-cors pyjwt
python app.py
# 访问 http://127.0.0.1:5000
```

## 部署

参见 `/etc/systemd/system/zhongyi.service` (服务器端)。

## 历史 (Laravel/Flutter 规划)

`backend/` 和 `frontend/` 目录包含原始的 Laravel PHP 后端和 Flutter 前端规划
(未完成，仅供参考，当前运行版本为 Flask + 单页 HTML)。
