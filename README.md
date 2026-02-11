# Video Uploader Skill

A Manus skill for automated video uploads to major Chinese and international social media platforms.

## Supported Platforms

- **Douyin (抖音)** - China's leading short video platform
- **Kuaishou (快手)** - Popular Chinese short video platform  
- **Xiaohongshu (小红书)** - Chinese lifestyle and social commerce platform
- **TikTok** - International short video platform
- **Tencent Video / WeChat Channels (视频号)** - WeChat's integrated video platform

## Features

- Browser automation using Playwright
- Cookie-based authentication with auto-renewal
- Scheduled publishing support
- Platform-specific features (thumbnails, product links, categories)
- Unified command-line interface
- Headless and visible browser modes

## Installation

1. Install Python dependencies:
```bash
pip3 install -r references/requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium firefox
```

## Quick Start

Upload a video to Douyin:
```bash
python scripts/upload_video.py \
  --platform douyin \
  --title "My Video Title" \
  --video /path/to/video.mp4 \
  --tags "tag1,tag2,tag3" \
  --account /path/to/douyin_cookie.json
```

## Documentation

See `SKILL.md` for complete documentation including:
- Detailed platform information
- Authentication and cookie management
- Advanced usage examples
- Troubleshooting guide

## Source

This skill is extracted from the [social-auto-upload](https://github.com/dreammis/social-auto-upload) project, containing only the core browser automation and upload functionality needed for OpenClaw integration.

## License

This skill is based on code from social-auto-upload project. Please refer to the original project for licensing information.
