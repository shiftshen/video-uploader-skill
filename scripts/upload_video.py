#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified video upload script for multiple platforms
Supports: Douyin, Kuaishou, Xiaohongshu, TikTok, Tencent Video (WeChat Channels)
"""
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from douyin_uploader.main import DouYinVideo, douyin_setup
from ks_uploader.main import KSVideo, ks_setup
from tk_uploader.main import TiktokVideo, tiktok_setup
from tencent_uploader.main import TencentVideo, weixin_setup


async def upload_to_douyin(title, video_path, tags, publish_date, account_file, thumbnail_path=None, product_link='', product_title=''):
    """Upload video to Douyin (抖音)"""
    # Setup and verify cookie
    if not await douyin_setup(account_file, handle=True):
        print("Failed to setup Douyin account")
        return False
    
    # Create video object and upload
    video = DouYinVideo(
        title=title,
        file_path=video_path,
        tags=tags,
        publish_date=publish_date,
        account_file=account_file,
        thumbnail_path=thumbnail_path,
        productLink=product_link,
        productTitle=product_title
    )
    await video.main()
    return True


async def upload_to_kuaishou(title, video_path, tags, publish_date, account_file):
    """Upload video to Kuaishou (快手)"""
    # Setup and verify cookie
    if not await ks_setup(account_file, handle=True):
        print("Failed to setup Kuaishou account")
        return False
    
    # Create video object and upload
    video = KSVideo(
        title=title,
        file_path=video_path,
        tags=tags,
        publish_date=publish_date,
        account_file=account_file
    )
    await video.main()
    return True


async def upload_to_tiktok(title, video_path, tags, publish_date, account_file):
    """Upload video to TikTok"""
    # Setup and verify cookie
    if not await tiktok_setup(account_file, handle=True):
        print("Failed to setup TikTok account")
        return False
    
    # Create video object and upload
    video = TiktokVideo(
        title=title,
        file_path=video_path,
        tags=tags,
        publish_date=publish_date,
        account_file=account_file
    )
    await video.main()
    return True


async def upload_to_tencent(title, video_path, tags, publish_date, account_file, category=None):
    """Upload video to Tencent Video / WeChat Channels (视频号)"""
    # Setup and verify cookie
    if not await weixin_setup(account_file, handle=True):
        print("Failed to setup Tencent/WeChat account")
        return False
    
    # Create video object and upload
    video = TencentVideo(
        title=title,
        file_path=video_path,
        tags=tags,
        publish_date=publish_date,
        account_file=account_file,
        category=category
    )
    await video.main()
    return True


def parse_publish_date(date_str):
    """Parse publish date string to datetime object"""
    if not date_str or date_str == "0":
        return 0
    
    # Try different date formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}. Use format: YYYY-MM-DD HH:MM:SS")


async def main():
    parser = argparse.ArgumentParser(description='Upload video to social media platforms')
    parser.add_argument('--platform', required=True, 
                        choices=['douyin', 'kuaishou', 'tiktok', 'tencent', 'xhs'],
                        help='Target platform')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--video', required=True, help='Path to video file')
    parser.add_argument('--tags', required=True, help='Comma-separated tags (e.g., "tag1,tag2,tag3")')
    parser.add_argument('--account', required=True, help='Path to account cookie file')
    parser.add_argument('--publish-date', default='0', help='Publish date (YYYY-MM-DD HH:MM:SS) or 0 for immediate')
    parser.add_argument('--thumbnail', help='Path to thumbnail image (Douyin only)')
    parser.add_argument('--product-link', help='Product link (Douyin only)')
    parser.add_argument('--product-title', help='Product title (Douyin only)')
    parser.add_argument('--category', help='Video category (Tencent only)')
    
    args = parser.parse_args()
    
    # Parse tags
    tags = [tag.strip() for tag in args.tags.split(',')]
    
    # Parse publish date
    publish_date = parse_publish_date(args.publish_date)
    
    # Verify video file exists
    if not Path(args.video).exists():
        print(f"Error: Video file not found: {args.video}")
        return
    
    # Verify account file exists
    if not Path(args.account).exists():
        print(f"Warning: Account file not found: {args.account}")
        print("Will attempt to create it through login process...")
    
    # Upload to platform
    try:
        if args.platform == 'douyin':
            await upload_to_douyin(
                title=args.title,
                video_path=args.video,
                tags=tags,
                publish_date=publish_date,
                account_file=args.account,
                thumbnail_path=args.thumbnail,
                product_link=args.product_link or '',
                product_title=args.product_title or ''
            )
        elif args.platform == 'kuaishou':
            await upload_to_kuaishou(
                title=args.title,
                video_path=args.video,
                tags=tags,
                publish_date=publish_date,
                account_file=args.account
            )
        elif args.platform == 'tiktok':
            await upload_to_tiktok(
                title=args.title,
                video_path=args.video,
                tags=tags,
                publish_date=publish_date,
                account_file=args.account
            )
        elif args.platform == 'tencent':
            await upload_to_tencent(
                title=args.title,
                video_path=args.video,
                tags=tags,
                publish_date=publish_date,
                account_file=args.account,
                category=args.category
            )
        elif args.platform == 'xhs':
            print("Xiaohongshu (小红书) upload is not yet implemented in this script")
            print("Please refer to the xhs_uploader module for implementation details")
            return
        
        print(f"\n✅ Successfully uploaded to {args.platform}")
        
    except Exception as e:
        print(f"\n❌ Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
