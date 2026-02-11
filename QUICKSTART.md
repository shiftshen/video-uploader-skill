# Video Uploader - Quick Start Guide

## First Time Setup

### 1. Create Credentials Directory

```bash
mkdir -p ~/.openclaw/credentials/douyin
mkdir -p ~/.openclaw/credentials/tiktok
mkdir -p ~/.openclaw/credentials/kuaishou
mkdir -p ~/.openclaw/credentials/tencent
```

### 2. Install Dependencies

```bash
pip3 install -r references/requirements.txt
playwright install chromium firefox
```

## Login (First Time)

```bash
# Login to Douyin - opens browser for manual login
cd ~/Documents/trae/openclaw/state/workspace/skills/douyin-publish
python3 bin/douyin --title "test" --video /tmp/test.mp4 --tags test
# → Browser opens, login manually, cookies auto-saved

# Login to TikTok
python3 bin/tiktok --title "test" --video /tmp/test.mp4 --tags test
```

## Usage

### Douyin
```bash
python3 bin/douyin \
  --title "我的视频标题" \
  --video ~/Videos/my_video.mp4 \
  --tags 旅行,风景,治愈 \
  --thumbnail ~/cover.jpg \
  --product-link https://... \
  --product-title "商品名"
```

### TikTok
```bash
python3 bin/tiktok \
  --title "My viral video" \
  --video ~/Videos/my_video.mp4 \
  --tags viral,trending,fyp \
  --publish-date "2026-02-15 12:00:00"
```

### Unified Command (All Platforms)
```bash
python3 bin/video-uploader upload \
  --platform douyin \
  --title "标题" \
  --video ~/video.mp4 \
  --tags tag1,tag2
```

## File Locations

| Platform | Cookie Path |
|----------|-------------|
| Douyin | `~/.openclaw/credentials/douyin/storage.json` |
| TikTok | `~/.openclaw/credentials/tiktok/storage.json` |
| Kuaishou | `~/.openclaw/credentials/kuaishou/storage.json` |
| Tencent | `~/.openclaw/credentials/tencent/storage.json` |

## Platform Features

| Platform | Cover | Product Link | Schedule | Sync |
|----------|-------|--------------|----------|------|
| Douyin | ✅ | ✅ | ✅ | ✅ Toutiao/Xigua |
| TikTok | ❌ | ❌ | ✅ | ❌ |
| Kuaishou | ❌ | ❌ | ✅ | ❌ |
| Tencent | ❌ | ❌ | ✅ | ❌ |

## Troubleshooting

### "Cookie expired" or login fails
Re-run the upload command - it will auto-prompt for new login.

### Video upload stuck
Check that browser is closed, then retry.

### Platform UI changed
The script may need updates. Check GitHub for latest version.

## GitHub

https://github.com/shiftshen/video-uploader-skill
