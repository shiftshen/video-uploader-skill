# Platform-Specific Details

This document provides platform-specific information for video uploads.

## Douyin (抖音)

**Upload URL**: `https://creator.douyin.com/creator-micro/content/upload`

**Cookie Authentication**: 
- Cookie file is stored in JSON format (Playwright storage state)
- Must include valid session cookies for `creator.douyin.com`

**Features**:
- Title: Up to 30 characters
- Description: Supports hashtags with `#` prefix
- Thumbnail: Optional vertical cover image
- Product Link: Optional shopping cart integration
- Schedule: Supports scheduled publishing
- Third-party sync: Can sync to Toutiao/Xigua

**Special Notes**:
- Two page versions exist (v1 and v2), script handles both
- Video must finish uploading before setting other options
- Uses Chromium browser

## Kuaishou (快手)

**Upload URL**: `https://cp.kuaishou.com/article/publish/video`

**Cookie Authentication**:
- Cookie file is stored in JSON format (Playwright storage state)
- Must include valid session cookies for `cp.kuaishou.com`

**Features**:
- Title: Entered in description field
- Tags: Maximum 3 hashtags
- Schedule: Supports scheduled publishing

**Special Notes**:
- Uses Chromium browser
- Requires confirmation dialog for publishing

## TikTok

**Upload URL**: `https://www.tiktok.com/tiktokstudio/upload`

**Cookie Authentication**:
- Cookie file is stored in JSON format (Playwright storage state)
- Must include valid session cookies for `www.tiktok.com`

**Features**:
- Title: Entered in content editor
- Tags: Hashtags with `#` prefix
- Schedule: Supports scheduled publishing (time in 5-minute increments)

**Special Notes**:
- Uses Firefox browser (not Chromium)
- Two UI versions: iframe-based and direct
- Schedule time picker uses specific hour/minute selection

## Tencent Video / WeChat Channels (视频号)

**Upload URL**: `https://channels.weixin.qq.com/platform/post/create`

**Cookie Authentication**:
- Cookie file is stored in JSON format (Playwright storage state)
- Must include valid session cookies for `channels.weixin.qq.com`

**Features**:
- Title: Entered in content editor
- Tags: Hashtags with `#` prefix
- Short Title: 6-16 characters, special formatting rules
- Collections: Can add to existing collections
- Original: Can declare original content with category
- Schedule: Supports scheduled publishing

**Special Notes**:
- Uses system Chrome (requires LOCAL_CHROME_PATH)
- Short title has character restrictions
- Original declaration requires category selection

## Xiaohongshu (小红书)

**Upload URL**: `https://creator.xiaohongshu.com/publish/publish`

**Cookie Authentication**:
- Requires `a1` and `web_session` cookies
- Uses signature service for API requests

**Features**:
- Supports both image and video posts
- Title and description
- Hashtags and location tags
- Schedule publishing

**Special Notes**:
- Requires separate signature service (Flask server)
- More complex API-based upload process
- Uses Chromium with stealth mode
