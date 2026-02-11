# OpenClaw 集成 Video Uploader Skill - 快速开始

## 📦 项目信息

**GitHub 仓库**：https://github.com/lijingpan/video-uploader

**功能**：自动上传视频到抖音、快手、TikTok、视频号、小红书

## 🚀 在 OpenClaw 中添加此 Skill

### 步骤 1：克隆仓库到 Skills 目录

```bash
# 进入 OpenClaw 的 skills 目录
cd /path/to/openclaw/skills

# 克隆仓库
git clone https://github.com/lijingpan/video-uploader.git

# 进入目录
cd video-uploader
```

### 步骤 2：安装依赖

```bash
# 安装 Python 依赖
pip install -r references/requirements.txt

# 安装 Playwright 浏览器
playwright install chromium firefox
```

### 步骤 3：验证安装

```bash
# 检查 SKILL.md 是否存在
ls -l SKILL.md

# 查看 skill 信息
head -10 SKILL.md
```

## 🎯 OpenClaw 使用示例

### 示例 1：让 OpenClaw 上传视频

**你说**：
```
帮我把 /path/to/video.mp4 上传到抖音，标题是"美食探店"，标签是"美食,探店,北京"
```

**OpenClaw 会**：
1. 读取 video-uploader skill
2. 检查是否有 Cookie 文件
3. 如果没有，打开浏览器让你扫码登录
4. 执行上传

### 示例 2：批量上传到多个平台

**你说**：
```
把这个视频同时上传到抖音、TikTok 和快手，标题用"每日分享"，标签自动生成
```

**OpenClaw 会**：
1. 读取 video-uploader skill
2. 生成批量上传配置
3. 依次上传到三个平台

### 示例 3：从 Google Drive 自动上传

**你说**：
```
每天从我的 Google Drive 文件夹下载视频并上传到抖音
```

**OpenClaw 会**：
1. 集成 Google Drive API
2. 设置定时任务
3. 每天自动下载和上传

## 📋 Skill 目录结构

```
video-uploader/
├── SKILL.md                    # ← OpenClaw 会读取这个文件
├── OPENCLAW_INTEGRATION.md     # ← OpenClaw 集成说明
├── README.md                   # 项目说明
├── scripts/                    # 可执行脚本
│   ├── upload_video.py         # 直接上传
│   ├── upload_from_config.py   # 配置文件上传
│   ├── generate_upload_config.py # 配置生成
│   └── [平台上传器]/           # 各平台实现
├── references/                 # 参考文档
│   ├── requirements.txt        # Python 依赖
│   ├── platform_fields.md      # 平台字段规范
│   └── platform_details.md     # 平台详细信息
└── templates/                  # 配置模板
```

## 🔧 核心脚本说明

### 1. 直接上传脚本

**文件**：`scripts/upload_video.py`

**用途**：命令行直接上传

**OpenClaw 调用方式**：
```python
subprocess.run([
    "python", "scripts/upload_video.py",
    "--platform", "douyin",
    "--title", title,
    "--video", video_path,
    "--tags", tags,
    "--account", cookie_path
])
```

### 2. 配置文件上传

**文件**：`scripts/upload_from_config.py`

**用途**：从 JSON/YAML 配置上传

**OpenClaw 调用方式**：
```python
# 1. 生成配置文件
config = {
    "platform": "douyin",
    "video": {...},
    "account": {...}
}
with open("config.json", "w") as f:
    json.dump(config, f)

# 2. 执行上传
subprocess.run([
    "python", "scripts/upload_from_config.py",
    "config.json"
])
```

### 3. 字段生成工具

**文件**：`scripts/generate_upload_config.py`

**用途**：从视频文件自动生成标题、标签

**OpenClaw 调用方式**：
```python
subprocess.run([
    "python", "scripts/generate_upload_config.py",
    "--platform", "douyin",
    "--video", video_path,
    "--output", "json"
])
```

## 🔐 Cookie 管理

### 首次使用流程

1. **OpenClaw 检测到没有 Cookie**
2. **自动打开浏览器**（非无头模式）
3. **用户扫码登录**
4. **Cookie 自动保存**到指定文件
5. **后续使用无需再次登录**（7-30天有效）

### Cookie 文件位置

建议在 OpenClaw 配置中设置：
```
/home/user/openclaw/cookies/
├── douyin_account.json
├── kuaishou_account.json
├── tiktok_account.json
├── tencent_account.json
└── xhs_account.json
```

## 🌐 支持的平台

| 平台 | 标识符 | 浏览器 | 特色功能 |
|------|--------|--------|---------|
| 抖音 | `douyin` | Chromium | 商品链接、缩略图 |
| 快手 | `kuaishou` | Chromium | 最多3个标签 |
| TikTok | `tiktok` | Firefox | 隐私设置 |
| 视频号 | `tencent` | Chromium | 原创声明、合集 |
| 小红书 | `xhs` | Chromium | 图文混合 |

## 📊 字段规范

### 所有平台通用字段

**必需**：
- `platform`: 平台标识符
- `title`: 视频标题
- `video_path`: 视频文件路径
- `tags`: 标签列表
- `account_file`: Cookie 文件路径

**可选**：
- `publish_date`: 定时发布时间（0 表示立即发布）
- `description`: 视频描述

### 平台特定字段

**抖音**：
- `thumbnail`: 缩略图路径
- `product_link`: 商品链接
- `product_title`: 商品标题

**TikTok**：
- `privacy`: 隐私设置（public/friends/private）
- `allow_comments`: 允许评论
- `allow_duet`: 允许合拍
- `allow_stitch`: 允许剪辑

**视频号**：
- `short_title`: 短标题（6-16字符）
- `is_original`: 原创声明
- `category`: 分类
- `collection_id`: 合集 ID

详细字段规范见：`references/platform_fields.md`

## 🤖 OpenClaw 工作流程

### 工作流 1：单个视频上传

```
用户输入
    ↓
OpenClaw 读取 SKILL.md
    ↓
解析用户意图（平台、标题、标签等）
    ↓
检查 Cookie 是否存在
    ↓
[如果不存在] 打开浏览器 → 用户登录 → 保存 Cookie
    ↓
调用 upload_video.py
    ↓
返回上传结果
```

### 工作流 2：批量上传

```
用户输入（多个平台）
    ↓
OpenClaw 读取 SKILL.md
    ↓
生成批量配置文件
    ↓
调用 upload_from_config.py --batch
    ↓
依次上传到各平台
    ↓
返回汇总结果
```

### 工作流 3：定时任务

```
用户设置定时任务
    ↓
OpenClaw 创建 cron/scheduler
    ↓
定时触发
    ↓
从 Google Drive 下载视频
    ↓
调用 video-uploader skill
    ↓
上传完成
```

## ⚠️ 重要注意事项

### 环境要求

**必需**：
- ✅ 图形界面环境（X Server）
- ✅ Python 3.8+
- ✅ Playwright 浏览器

**不支持**：
- ❌ 纯无头服务器（无 X11）
- ❌ Docker 容器（除非配置 X11 转发）

### 浏览器可见性

- 上传时浏览器窗口**会可见**
- 这是绕过平台检测的**必要条件**
- 不要使用无头模式

### Cookie 有效期

- Cookie 通常有效期 7-30 天
- 过期后需要重新登录
- OpenClaw 会自动检测并提示

## 🔧 故障排除

### 问题 1：OpenClaw 找不到 skill

**原因**：skill 目录位置不对

**解决**：
```bash
# 确保在正确的位置
ls /path/to/openclaw/skills/video-uploader/SKILL.md
```

### 问题 2：浏览器无法打开

**原因**：没有图形界面

**解决**：
- 在有桌面环境的系统运行
- 或配置 Xvfb 虚拟显示

### 问题 3：Cookie 过期

**原因**：Cookie 有效期到期

**解决**：
- 删除旧 Cookie 文件
- 重新运行脚本登录

### 问题 4：平台 UI 变化

**原因**：社交平台更新了界面

**解决**：
- 检查 GitHub 是否有更新
- 提交 Issue 报告问题

## 📞 获取更多帮助

- **完整文档**：查看 `SKILL.md`
- **字段规范**：查看 `references/platform_fields.md`
- **平台详情**：查看 `references/platform_details.md`
- **OpenClaw 集成**：查看 `OPENCLAW_INTEGRATION.md`
- **问题反馈**：GitHub Issues

## 🎉 开始使用

现在你可以在 OpenClaw 中使用自然语言命令上传视频了！

**试试这些命令**：

```
"帮我把这个视频上传到抖音"
"同时上传到抖音和TikTok"
"每天自动从Google Drive上传视频"
"定时明天下午6点发布这个视频"
```

OpenClaw 会自动调用 video-uploader skill 完成任务！🚀
