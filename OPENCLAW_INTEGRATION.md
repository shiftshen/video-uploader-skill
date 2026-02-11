# OpenClaw 集成指南

## 📦 项目说明

这是一个用于自动上传视频到多个社交媒体平台的 Manus/OpenClaw skill。

**支持平台**：
- 抖音 (Douyin)
- 快手 (Kuaishou)
- TikTok
- 视频号 (WeChat Channels / Tencent Video)
- 小红书 (Xiaohongshu)

## 🚀 在 OpenClaw 中添加此 Skill

### 方法 1：从 GitHub 直接添加

```bash
# 在 OpenClaw 的 skills 目录中
cd /path/to/openclaw/skills

# 克隆此仓库
git clone https://github.com/shiftshen/video-uploader.git

# 安装依赖
cd video-uploader
pip install -r references/requirements.txt
playwright install chromium firefox
```

### 方法 2：手动下载

1. 下载此仓库的 ZIP 文件
2. 解压到 OpenClaw 的 `skills` 目录
3. 重命名文件夹为 `video-uploader`
4. 安装依赖（见上）

## 📋 Skill 结构

```
video-uploader/
├── SKILL.md                    # Skill 主文档（OpenClaw 会读取）
├── README.md                   # 项目说明
├── OPENCLAW_INTEGRATION.md     # 本文件
├── CHECKLIST.md                # 验收清单
├── scripts/                    # 可执行脚本
│   ├── upload_video.py         # 直接上传脚本
│   ├── upload_from_config.py   # 配置文件上传
│   ├── generate_upload_config.py # 配置生成工具
│   ├── douyin_uploader/        # 抖音上传器
│   ├── ks_uploader/            # 快手上传器
│   ├── tk_uploader/            # TikTok 上传器
│   ├── tencent_uploader/       # 视频号上传器
│   ├── xhs_uploader/           # 小红书上传器
│   └── utils/                  # 工具模块
├── references/                 # 参考文档
│   ├── requirements.txt        # Python 依赖
│   ├── platform_fields.md      # 平台字段规范
│   └── platform_details.md     # 平台详细信息
└── templates/                  # 配置模板
    ├── upload_config_template.json
    └── upload_config_template.yaml
```

## 🎯 OpenClaw 使用示例

### 示例 1：上传单个视频到抖音

```
用户: 帮我把这个视频上传到抖音，标题是"美食探店"，标签是"美食,探店,北京"

OpenClaw 会：
1. 读取 video-uploader skill
2. 使用 scripts/upload_video.py
3. 自动生成配置
4. 执行上传
```

### 示例 2：批量上传到多个平台

```
用户: 把这个视频同时上传到抖音、TikTok 和快手

OpenClaw 会：
1. 读取 video-uploader skill
2. 使用 scripts/generate_upload_config.py 生成配置
3. 使用 scripts/upload_from_config.py --batch 批量上传
```

### 示例 3：从 Google Drive 自动上传

```
用户: 每天从我的 Google Drive 下载视频并上传到抖音

OpenClaw 会：
1. 集成 Google Drive API
2. 下载视频
3. 使用 video-uploader skill 上传
4. 设置定时任务
```

## ⚙️ 配置要求

### 环境要求

**必需**：
- Python 3.8+
- 图形界面环境（X Server）
- Playwright 浏览器

**可选**：
- Google Drive API 凭证（如需集成）
- 定时任务系统（cron 或 Manus scheduler）

### 首次使用

1. **准备 Cookie 目录**：
```bash
mkdir -p /home/ubuntu/cookies
```

2. **首次登录**：
运行上传脚本时会自动打开浏览器，扫码登录后 Cookie 自动保存。

3. **后续使用**：
使用相同的 Cookie 文件无需再次登录（有效期 7-30 天）。

## 📖 核心功能

### 1. 字段自动生成

从视频文件自动生成标题、标签、描述：

```bash
python scripts/generate_upload_config.py \
  --platform douyin \
  --video /path/to/video.mp4 \
  --output json
```

### 2. 直接上传

```bash
python scripts/upload_video.py \
  --platform douyin \
  --title "视频标题" \
  --video /path/to/video.mp4 \
  --tags "标签1,标签2,标签3" \
  --account /path/to/cookie.json
```

### 3. 配置文件上传

```bash
# 单个上传
python scripts/upload_from_config.py config.json

# 批量上传
python scripts/upload_from_config.py batch.json --batch
```

### 4. 定时发布

```bash
python scripts/generate_upload_config.py \
  --platform douyin \
  --video /path/to/video.mp4 \
  --schedule-days 1 \
  --schedule-hour 18 \
  --output-file config.json
```

## 🔧 OpenClaw 集成模式

### 模式 1：命令行调用

OpenClaw 直接调用脚本：

```python
import subprocess

result = subprocess.run([
    "python", "scripts/upload_video.py",
    "--platform", "douyin",
    "--title", "AI 生成的标题",
    "--video", video_path,
    "--tags", "AI,自动化",
    "--account", cookie_path
], capture_output=True)
```

### 模式 2：配置文件生成

OpenClaw 生成配置文件后调用：

```python
import json

# 1. 生成配置
config = {
    "platform": "douyin",
    "video": {
        "path": video_path,
        "title": ai_generated_title,
        "tags": ai_generated_tags
    },
    "account": {
        "cookie_file": cookie_path
    }
}

# 2. 保存配置
with open("/tmp/upload_config.json", "w") as f:
    json.dump(config, f)

# 3. 执行上传
subprocess.run([
    "python", "scripts/upload_from_config.py",
    "/tmp/upload_config.json"
])
```

### 模式 3：程序化集成

OpenClaw 直接导入模块：

```python
import sys
sys.path.insert(0, "/path/to/video-uploader/scripts")

from douyin_uploader.main import DouYinVideo, douyin_setup
import asyncio

async def upload():
    await douyin_setup(cookie_path, handle=True)
    
    video = DouYinVideo(
        title=title,
        file_path=video_path,
        tags=tags,
        publish_date=0,
        account_file=cookie_path
    )
    
    await video.main()

asyncio.run(upload())
```

## 🌐 平台特定功能

### 抖音
- ✅ 缩略图上传
- ✅ 商品链接
- ✅ 第三方同步（头条/西瓜）
- ✅ 定时发布

### 快手
- ✅ 最多 3 个标签
- ✅ 定时发布
- ✅ 确认对话框处理

### TikTok
- ✅ 隐私设置
- ✅ 互动权限（评论/合拍/剪辑）
- ✅ 定时发布（5分钟增量）

### 视频号
- ✅ 短标题格式化
- ✅ 原创声明
- ✅ 合集管理
- ✅ 分类选择

### 小红书
- ✅ 视频和图文混合
- ✅ 封面图上传
- ✅ 地理位置
- ⚠️ 需要独立签名服务

## 🔒 安全和隐私

### Cookie 管理
- Cookie 文件包含登录信息，请妥善保管
- 建议使用独立目录存储
- 定期更新过期的 Cookie

### API 凭证
- Google Drive API 凭证不要泄露
- 使用环境变量存储敏感信息

### 日志脱敏
- 日志中不包含敏感信息
- 定期清理日志文件

## 📊 支持的平台对比

| 平台 | 浏览器 | 标题长度 | 标签限制 | 定时发布 | 特殊功能 |
|------|--------|---------|---------|---------|---------|
| 抖音 | Chromium | 30字符 | 无限制 | ✅ | 商品链接 |
| 快手 | Chromium | 无限制 | 最多3个 | ✅ | - |
| TikTok | Firefox | 无限制 | 无限制 | ✅ | 隐私设置 |
| 视频号 | Chromium | 无限制 | 无限制 | ✅ | 原创/合集 |
| 小红书 | Chromium | 无限制 | 无限制 | ✅ | 图文混合 |

## 🐛 故障排除

### Cookie 过期
**问题**：上传失败，提示需要登录
**解决**：删除旧 Cookie 文件，重新运行脚本登录

### 浏览器未找到
**问题**：Playwright 浏览器未安装
**解决**：运行 `playwright install chromium firefox`

### 页面结构变化
**问题**：平台 UI 更新导致脚本失败
**解决**：检查 GitHub 是否有更新，或提交 Issue

### 无头模式失败
**问题**：在无头服务器运行失败
**解决**：使用带桌面环境的服务器，或配置 Xvfb

## 📞 获取帮助

- **文档**：查看 `SKILL.md` 获取完整文档
- **字段规范**：查看 `references/platform_fields.md`
- **示例**：查看 `templates/` 目录
- **问题反馈**：在 GitHub 提交 Issue

## 🔄 版本说明

**当前版本**：1.0.0

**更新内容**：
- ✅ 支持 5 个主流平台
- ✅ 完整的浏览器反检测配置
- ✅ 字段自动生成
- ✅ 批量上传
- ✅ 定时发布
- ✅ OpenClaw 集成支持

## 📝 许可证

基于 [social-auto-upload](https://github.com/dreammis/social-auto-upload) 项目提取和改进。

---

**OpenClaw 集成完成后，你就可以通过自然语言命令上传视频了！** 🎉
