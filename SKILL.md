# Multi-Platform Video Uploader Skill

Automated video upload to Chinese and international social media platforms using Playwright browser automation.

## Supported Platforms

| Platform | Name | Description | Status |
|----------|------|-------------|--------|
| douyin | 抖音 | China's leading short video platform | ✅ Ready |
| kuaishou | 快手 | Popular Chinese short video platform | ✅ Ready |
| tiktok | TikTok | International short video platform | ✅ Ready |
| tencent | 视频号 | WeChat Channels video platform | ✅ Ready |
| xiaohongshu | 小红书 | Lifestyle platform | ⚠️ Manual |

## Features

- **Browser Automation**: Playwright-based (Chromium/Firefox)
- **Cookie Auth**: JSON storage state with auto-renewal
- **Scheduled Publishing**: Support for future upload times
- **Platform-specific**: Optimized for each platform's UI
- **Unified Interface**: Single command for all platforms

## Installation

```bash
# Install dependencies
pip3 install -r references/requirements.txt

# Install Playwright browsers
playwright install chromium firefox
```

## Quick Start

### Upload to Douyin

```bash
# Using simplified command
douyin --title "My Video" --video ~/video.mp4 --tags fun,travel

# Or with full options
video-uploader upload \
  --platform douyin \
  --title "My Video" \
  --video ~/video.mp4 \
  --tags fun,travel \
  --thumbnail ~/cover.jpg \
  --product-link https://... \
  --product-title "Product Name"
```

### Upload to TikTok

```bash
# Simplified command
tiktok --title "My TikTok" --video ~/video.mp4 --tags viral,trending

# With scheduling
video-uploader upload \
  --platform tiktok \
  --title "My Video" \
  --video ~/video.mp4 \
  --tags viral \
  --publish-date "2026-02-15 12:00:00"
```

### Unified Command

```bash
# List platforms
video-uploader platforms

# Upload to any platform
video-uploader upload --platform douyin --title "..." --video ... --tags ...

# Login to platform
video-uploader login --platform tiktok
```

## Credentials

Credentials are stored in JSON format (Playwright storage state):

| Platform | Default Path |
|----------|--------------|
| Douyin | `~/.openclaw/credentials/douyin/storage.json` |
| Kuaishou | `~/.openclaw/credentials/kuaishou/storage.json` |
| TikTok | `~/.openclaw/credentials/tiktok/storage.json` |
| Tencent | `~/.openclaw/credentials/tencent/storage.json` |

## Platform-Specific Options

### Douyin

- `--thumbnail`: Cover image path
- `--product-link`: Shopping cart product URL
- `--product-title`: Product short title

### TikTok

- `--publish-date`: Schedule time (YYYY-MM-DD HH:MM:SS)

### Tencent/WeChat

- `--category`: Video category

## Workflow

1. **First Time**: Runs browser for manual login, saves cookies
2. **Subsequent**: Uses stored cookies for auto-upload
3. **Cookie Update**: Automatically saves fresh cookies after upload

## Troubleshooting

### Cookie Expired

```bash
# Re-login
video-uploader login --platform douyin
```

### Upload Fails

- Check video format/size requirements
- Ensure browser is not already open
- Try with `--headless false` for debugging

### Platform UI Changed

The script may need updates if platform UI changes significantly.
Check GitHub for latest version: https://github.com/shiftshen/video-uploader-skill

## Code Structure

```
douyin-publish/
├── bin/
│   ├── video-uploader    # Unified multi-platform uploader
│   ├── douyin            # Douyin-specific shortcut
│   └── tiktok            # TikTok-specific shortcut
├── scripts/
│   ├── douyin_uploader/  # Douyin implementation
│   ├── ks_uploader/      # Kuaishou implementation
│   ├── tk_uploader/      # TikTok implementation
│   ├── tencent_uploader/ # Tencent/WeChat implementation
│   └── xhs_uploader/     # Xiaohongshu (manual only)
├── references/
│   ├── platform_details.md   # Platform-specific info
│   ├── platform_fields.md    # Field requirements
│   └── requirements.txt      # Python dependencies
└── templates/            # Cookie/account templates
```

## Based On

This skill is extracted from [social-auto-upload](https://github.com/dreammis/social-auto-upload) project.
