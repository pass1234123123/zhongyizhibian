# 中医智伴 Android APK 构建指南

## 项目信息

| 项目 | 内容 |
|------|------|
| 应用名称 | 中医智伴 |
| 包名 | `com.zhongyi.zhiban` |
| 版本 | 1.0.0 |
| Cordova项目路径 | `android-app/` |
| API服务器地址 | `http://192.168.11.138:5000` |

---

## 方式一：本地构建（需要 Android SDK + Java JDK）

### 前置要求

1. **Java JDK 17+**
   - 下载：https://adoptium.net/
   - 安装后设置环境变量 `JAVA_HOME`

2. **Android Studio**（含 Android SDK）
   - 下载：https://developer.android.com/studio
   - 安装 SDK Platform 和 Build Tools
   - 设置环境变量 `ANDROID_HOME`

3. **Node.js 18+**
   - 下载：https://nodejs.org/

### 构建步骤

```bash
# 1. 进入项目目录
cd android-app

# 2. 安装 Cordova
npm install -g cordova

# 3. 添加 Android 平台（已添加，如出错可重加）
cordova platform rm android
cordova platform add android

# 4. 构建 APK
cordova build android

# APK 输出路径：
# android-app/platforms/android/app/build/outputs/apk/debug/
```

### 常见问题

- **SDK not found**: 设置 `ANDROID_HOME` 或 `ANDROID_SDK_ROOT` 环境变量
- **Java not found**: 检查 `JAVA_HOME` 环境变量
- **Gradle 下载慢**: 使用 Gradle 镜像

---

## 方式二：修改 API 服务器地址

默认 API 地址为 `http://192.168.11.138:5000`。
如需修改，编辑 `android-app/www/js/app.js`，找到开头：

```js
var API_BASE = 'http://192.168.11.138:5000';
```

改为你的服务器地址后重新构建。

---

## 方式三：PWA 安装（无需构建）

在 Android 手机上用 Chrome 打开

**http://192.168.11.138:5000**

然后点菜单 → "添加到主屏幕" 即可。

---

## 项目文件结构

```
zhongyizhiban/
  app.py              # Flask 后端
  models.py           # 数据库模型
  templates/
    index.html        # 前端页面
    admin.html        # 独立后台管理页面
  static/
    css/style.css     # 样式
    js/app.js         # JavaScript（前端逻辑）
    manifest.json     # PWA 清单文件（支持安装到桌面）
    icon-192.png      # APP 图标 192x192
    icon-512.png      # APP 图标 512x512
  android-app/
    config.xml        # Cordova 配置（包名: com.zhongyi.zhiban）
    www/
      index.html      # 入口页面
      css/style.css   # 样式
      js/app.js       # 已适配远程 API 的 JS
      img/
        icon-192.png  # APP 图标
        icon-512.png  # APP 图标
      manifest.json   # PWA 清单
    platforms/android/ # Android 平台文件（已添加）
```
