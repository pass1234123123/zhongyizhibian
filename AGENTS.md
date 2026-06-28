 # 关于本项目（AI 助手备忘录）

 > 最后更新：2026-06-27
 > 项目路径：F:\AI\codex\zhongyizhiban

 ---

 ## 你是谁

 你叫**镇华**，是这个项目的主人。你对编程技术不是很精通，所以跟你交流要用大白话，少用技术术语。

 ---

 ## 这个项目是做什么的

 **中医智慧平台**（也叫"中医智伴"），是一个中医治疗方案查询与分享网站。用户可以浏览各类疾病的治疗方案（针灸、中药方剂、拔罐、推拿、食疗等），也可以上传自己的中医资料，经过 AI 整理和人工审核后发布出来，供大家付费学习。

 简单说：就是一个中医版的"知识付费平台"，有人分享方子，有人花钱学习。

 ---

 ## 当前运行的技术方案

 目前真正在跑的是 Python 版本，已经部署到服务器上了：

 - **后端**：Python + Flask（轻量级网页框架）+ SQLite（数据库文件，不需要额外安装数据库软件）
 - **前端**：单页 HTML + 原生 JavaScript（所有页面写在一个 HTML 文件里）
 - **认证方式**：JWT Token（一种"令牌"，登录后拿到的凭证，带着它就能访问需要登录的功能）
 - **部署地址**：http://103.73.161.36:5000

 直接用浏览器打开就能用，不需要装 App。

 ---

 ## 项目文件结构

 ```
 zhongyizhiban/
 ├── app.py              # 后端主程序（有 25 个 API 接口）
 ├── models.py           # 数据库定义 + 初始数据（11 张表）
 ├── config.py           # 配置文件（密钥、数据库路径）
 ├── run.py              # 本地启动脚本
 ├── test_api.py         # 接口自动测试脚本
 ├── templates/
 │   ├── index.html      # 前端页面（含全部 JS 代码）
 │   └── app.js          # 旧文件，内容已合并到 index.html
 ├── static/             # 图片、样式等静态资源
 ├── uploads/            # 用户上传的文件存放目录
 ├── demo.html / demo.js # 最早的原始版本原型
 ├── zhongyi.db          # SQLite 数据库文件
 ├── 产品开发文档.md       # 完整的产品需求文档
 ├── backend/            # Laravel 版后端（规划阶段，未完成）
 ├── frontend/           # Flutter 版前端（规划阶段，骨架搭了一半）
 └── docs/
     ├── 产品开发文档.md   # 另一份产品需求文档备存
     └── 开发计划.md       # 分阶段的开发执行计划
 ```

 ---

 ## 核心功能一览

 | 功能 | 说明 |
 |------|------|
 | 疾病分类浏览 | 13 个科室分类（内科/外科/妇科/儿科等），每个分类下有具体疾病 |
 | 治疗方案查询 | 按疾病名称搜索，按治疗类型筛选（针灸/方剂/拔罐等） |
 | 治疗方案详情 | 免费看预览，付费后看完整内容（模拟支付，不真花钱） |
 | 疗效反馈 | 买过的人可以打分（1-5星）、写评价、选有效/无效 |
 | 内容上传 | 用户粘贴文字上传，系统模拟 AI 处理，等待管理员审核 |
 | 审核后台 | 管理员登录后审核上传内容，通过或驳回 |
 | 收藏功能 | 收藏喜欢的治疗方案 |
 | 积分系统 | 提交反馈得积分，上传内容被审核通过得积分 |
 | 模拟购买 | 点击购买按钮即可解锁完整内容，不用真花钱 |

 ---

 ## 管理员账号

 - 手机号：`13800000000`
 - 密码：`admin123`
 - 线上地址：http://103.73.161.36:5000

 ---

 ## 本地怎么跑起来

 打开终端，输入以下命令：

 ```
 cd F:\AI\codex\zhongyizhiban
 pip install flask flask-cors pyjwt
 python app.py
 ```

 然后浏览器打开 http://127.0.0.1:5000 就能看到了。

 ---

 ## 数据库里有什么

 数据库（`zhongyi.db`）有 11 张表，首次启动会自动创建并填充数据：

 - **users** — 用户表（角色分 user / reviewer / admin）
 - **disease_categories** — 疾病分类（13 个科）
 - **diseases** — 疾病条目（约 60 种常见病，比如胃痛、感冒、失眠等）
 - **treatment_types** — 治疗类型（针灸、方剂内服、拔罐、推拿等）
 - **treatments** — 治疗方案（约 40 多个具体方案，含价格/评分/预览/完整内容）
 - **treatment_formulas** — 方剂明细（药材组成/用法/注意事项）
 - **treatment_acupoints** — 针灸穴位明细（穴位/操作手法/疗程）
 - **treatment_type_relations** — 方案和类型的关联
 - **purchases** — 购买记录
 - **feedbacks** — 疗效反馈
 - **favorites** — 收藏记录
 - **points_log** — 积分流水（收支记录）
 - **uploads** — 上传内容（含 AI 处理结果和审核状态）

 ---

 ## 后端有哪些接口

 总共 25 个接口，大致分类如下：

 **公开接口（不需要登录）**
 - `GET /` — 首页（返回前端页面）
 - `GET /api/categories` — 获取疾病分类列表
 - `GET /api/diseases` — 获取疾病列表（可按分类筛选）
 - `GET /api/diseases/<id>` — 疾病详情
 - `GET /api/treatments` — 获取治疗方案列表（可按疾病/搜索/类型筛选）
 - `GET /api/treatments/types` — 获取所有治疗类型
 - `GET /api/feedback/<id>` — 查看某个治疗方案的反馈汇总
 - `POST /api/auth/register` — 注册
 - `POST /api/auth/login` — 登录

 **需要登录的接口**
 - `GET /api/auth/me` — 获取当前用户信息
 - `GET /api/treatments/<id>` — 治疗方案详情（含是否已购买）
 - `GET /api/treatments/<id>/full` — 已购买后查看完整内容
 - `POST /api/purchase` — 购买治疗方案（模拟支付）
 - `GET /api/purchases` — 我的购买记录
 - `POST /api/feedback` — 提交疗效反馈
 - `GET /api/favorites` — 我的收藏列表
 - `POST /api/favorites/toggle` — 收藏/取消收藏
 - `POST /api/upload` — 上传内容（文字或文件）
 - `GET /api/uploads` — 查看上传记录
 - `GET /api/points/log` — 积分流水

 **管理员接口**
 - `GET /api/admin/pending` — 待审核列表
 - `POST /api/admin/review` — 审核通过/驳回

 ---

 ## 关于 Laravel 和 Flutter 的部分

 项目里 `backend/` 和 `frontend/` 两个文件夹是早期规划的：

 - `backend/` — Laravel（PHP 框架）后端，搭了几个 Controller 和 Model 的骨架，**没做完**
 - `frontend/` — Flutter 前端（可以做成手机 App），搭了底部导航、登录页和路由框架，**也没做完**

 目前真正能跑的是 **Python Flask 版本**。Laravel 和 Flutter 部分如果以后你想做 App 版本可以参考，否则不用管它们。

 ---

 ## 代码阅读提示

 - `app.py` 是主文件，所有 API 接口都写在这里，约 27KB
 - `models.py` 负责建表和填充初始数据，约 25KB
 - 前端页面在 `templates/index.html`，全部写在一个文件里
 - `产品开发文档.md` 是最完整的需求文档，如果要加新功能可以查阅
