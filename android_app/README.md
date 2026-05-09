# 数学启明星 Android 应用

基于 Flutter + Flame 游戏引擎的数学学习应用。

## 环境要求

1. Flutter SDK 3.2+
2. Android Studio (用于 Android SDK 和模拟器)
3. JDK 17+

## 安装步骤

### 1. 安装 Flutter
下载 Flutter SDK: https://docs.flutter.dev/get-started/install/windows
解压到 `C:\flutter`，将 `C:\flutter\bin` 添加到系统 PATH

### 2. 安装 Android Studio
下载: https://developer.android.com/studio
安装时勾选 Android SDK 和 Android Virtual Device

### 3. 验证环境
```bash
flutter doctor
```
确保看到所有项目为 ✓（Android toolchain 和 Chrome）

### 4. 安装依赖
```bash
cd android_app
flutter pub get
```

### 5. 运行
```bash
# 连接真机或启动模拟器后：
flutter run

# 或直接构建 APK：
flutter build apk --release
```

## 项目结构

```
lib/
├── main.dart              # 入口 + MaterialApp
├── api/
│   ├── api_config.dart    # 服务器地址配置
│   └── api_client.dart    # API 请求客户端
├── game/
│   └── math_sprite.dart   # Flame 精灵组件（点击交互、动画）
├── screens/
│   ├── home_screen.dart    # 主页（精灵 + 统计 + 入口）
│   ├── diagnose_screen.dart # 诊断流程
│   ├── quiz_screen.dart    # 自由练习（红心系统）
│   └── parent_screen.dart  # 家长看板（PIN + 热力图）
└── widgets/
    └── question_card.dart  # 题目卡片（渐变 + 动画 + 选项）

assets/
├── images/                # 精灵图片资源
└── audio/                 # 音效文件
```

## 连接后端

编辑 `lib/api/api_config.dart` 中的 `baseUrl` 指向你的服务器地址。

## 核心技术栈

- **Flutter** — 跨平台 UI 框架
- **Flame** — 2D 游戏引擎（精灵渲染 + 粒子效果）
- **flutter_animate** — 声明式动画
- **http** — REST API 调用
- **vibration** — 触觉反馈
- **audioplayers** — 音效播放

## 现有后端 API

所有 API 端点保持不变，Android 前端直接调用现有后端。
后端地址: http://101.96.217.150
