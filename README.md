# Video Uploader Skill

自动上传视频到抖音、TikTok、视频号等平台的工具。

## 支持平台

| 平台 | 状态 | 说明 |
|------|------|------|
| **抖音** | ✅ 可用 | 自动上传、封面、标签、定时发布 |
| **TikTok** | ✅ 可用 | 自动上传、标签、定时发布 |
| **视频号** | ✅ 可用 | 需要手机扫码登录 |

## 文件位置

- **项目路径**: `~/.openclaw/workspace/skills/video-uploader-skill/`
- **上传脚本**: `scripts/upload_video.py`
- **抖音 Cookie**: `scripts/cookies/douyin_uploader/cookie.json`
- **TikTok Cookie**: `scripts/cookies/tk_uploader/cookie.json`

## 快速开始

### 上传视频

```bash
cd ~/.openclaw/workspace/skills/video-uploader-skill/scripts

# 抖音
PYTHONPATH=. python3 upload_video.py \
  --platform douyin \
  --title "视频标题" \
  --video ~/Videos/test.mp4 \
  --tags 标签1,标签2 \
  --thumbnail ~/Videos/cover.jpg \
  --account scripts/cookies/douyin_uploader/cookie.json

# TikTok
PYTHONPATH=. python3 upload_video.py \
  --platform tiktok \
  --title "Video Title" \
  --video ~/Videos/test.mp4 \
  --tags tag1,tag2 \
  --account scripts/cookies/tk_uploader/cookie.json
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--platform` | 平台 | `douyin`, `tiktok` |
| `--title` | 视频标题 | "我的视频" |
| `--video` | 视频文件路径 | `~/Videos/test.mp4` |
| `--tags` | 标签（逗号分隔） | `CNC,工业` |
| `--thumbnail` | 封面图片（仅抖音） | `~/Videos/cover.jpg` |
| `--account` | Cookie 文件路径 | 见上文 |

## 已知问题和解决方案

### 抖音

1. **封面设置弹窗遮挡发布按钮**
   - 现象：设置封面后弹窗不消失，无法点击发布
   - 解决：代码已添加多次关闭弹窗逻辑

2. **发布按钮被遮挡**
   - 现象：点击发布按钮时被弹窗遮挡
   - 解决：添加了 `close_popups()` 函数和 `force=True` 点击

### TikTok

1. **Joyride 导览弹窗遮挡**
   - 现象：页面显示新手引导遮罩，遮挡所有点击
   - 解决：代码已添加 JavaScript 强制移除遮罩 + `force=True` 点击

2. **上传状态检测失败**
   - 现象：等待上传完成但无法检测
   - 解决：改用 `data-e2e="post_video_button"` 选择器

3. **发布按钮选择器错误**
   - 现象：多个匹配元素导致超时
   - 解决：使用 `aria-disabled` 属性检测按钮状态

## 重要提示

1. **Cookie 维护**: Cookie 会自动更新，但请定期检查是否过期
2. **弹窗处理**: 每次运行脚本前确保浏览器没有手动打开的标签页
3. **视频大小**: TikTok 有大小限制，确保视频符合要求
4. **发布间隔**: 建议每次发布间隔至少几分钟，避免被风控

## 更新日志

### 2026-02-13
- 修复抖音横封面设置问题
- 修复 TikTok Joyride 弹窗遮挡问题
- 修复 TikTok 发布按钮点击问题
- 添加更多日志便于调试

## GitHub

https://github.com/shiftshen/video-uploader-skill
