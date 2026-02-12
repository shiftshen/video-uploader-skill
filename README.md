# Video Uploader Skill for OpenClaw

Multi-platform video upload automation for OpenClaw.

## Supported Platforms

| Platform | Status | PC Web | Login Method | Notes |
|----------|--------|--------|--------------|-------|
| **抖音** | ✅ Verified | ✅ | Cookie | Auto-upload working |
| **TikTok** | ✅ Verified | ✅ | Cookie | Auto-upload working |
| **视频号** | ✅ Verified | ✅ | QR Code | Auto-upload working |
| **快手** | ❌ Not Supported | ❌ | - | No PC creator center |

## Platform Details

### 抖音 (Douyin) ✅
- **Status**: Fully functional
- **Features**: Upload, thumbnail, tags, scheduling, AI-generated flag
- **Known Issue**: "内容由AI生成" option may not appear (UI changed)
- **Cookie**: `credentials/douyin/storage.json`

### TikTok ✅
- **Status**: Fully functional
- **Features**: Upload, tags, scheduling
- **Cookie**: `credentials/tiktok/storage.json`

### 视频号 (Tencent/WeChat) ✅
- **Status**: Fully functional
- **Features**: Upload, tags, short title, original declaration, scheduling
- **Login**: QR code on phone required
- **Cookie**: `credentials/tencent/storage.json`

### 快手 (Kuaishou) ❌
- **Status**: Not supported
- **Reason**: No PC creator center, only mobile app upload
- **Alternative**: Use mobile app or API (not implemented)

## Requirements

- Playwright
- Chromium browser
- Python 3.10+

```bash
pip3 install -r references/requirements.txt
playwright install chromium
```

## Installation

```bash
cd ~/Documents/trae/openclaw/state/workspace/skills/douyin-publish
```

## Usage

### Login (First Time)

```bash
# Login to Douyin
python3 bin/video-uploader upload --platform douyin --title "test" --video /tmp/test.mp4 --tags test

# Login to TikTok
python3 bin/video-uploader upload --platform tiktok --title "test" --video /tmp/test.mp4 --tags test

# Login to Tencent (QR code required)
python3 bin/video-uploader upload --platform tencent --title "test" --video /tmp/test.mp4 --tags test
```

### Upload Video

```bash
# Douyin
python3 bin/video-uploader upload \
  --platform douyin \
  --title "我的视频标题" \
  --video ~/Videos/my_video.mp4 \
  --tags 旅行,风景,治愈 \
  --ai-generated

# TikTok
python3 bin/video-uploader upload \
  --platform tiktok \
  --title "My viral video" \
  --video ~/Videos/my_video.mp4 \
  --tags viral,trending,fyp

# Tencent (Video号)
python3 bin/video-uploader upload \
  --platform tencent \
  --title "视频号标题" \
  --video ~/Videos/my_video.mp4 \
  --tags 科技,数码
```

## File Locations

| Platform | Credential Path |
|----------|-----------------|
| Douyin | `skills/douyin-publish/credentials/douyin/storage.json` |
| TikTok | `skills/douyin-publish/credentials/tiktok/storage.json` |
| Tencent | `skills/douyin-publish/credentials/tencent/storage.json` |

## Recent Changes (2026-02-12)

### Fixes
- Browser viewport: 1920x1080 for better visibility
- Popup handling: Improved close logic
- Upload flow: Optimized wait times
- TikTok: Fixed cookie timeout (domcontentloaded vs networkidle)

### Added
- AI-generated content flag for Douyin (UI integration pending)
- Video号 (Tencent) support
- Multi-platform upload from single command

## GitHub

https://github.com/shiftshen/video-uploader-skill

## License

MIT
