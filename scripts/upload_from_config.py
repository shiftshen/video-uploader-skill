#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload video from configuration file (JSON/YAML)
Supports batch uploads and advanced configuration
"""
import asyncio
import argparse
import json
import yaml
from pathlib import Path
from datetime import datetime
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from douyin_uploader.main import DouYinVideo, douyin_setup
from ks_uploader.main import KSVideo, ks_setup
from tk_uploader.main import TiktokVideo, tiktok_setup
from tencent_uploader.main import TencentVideo, weixin_setup


def load_config(config_path: str) -> dict:
    """
    Load configuration from JSON or YAML file
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    content = config_file.read_text(encoding='utf-8')
    
    # Try JSON first
    if config_file.suffix.lower() in ['.json']:
        return json.loads(content)
    
    # Try YAML
    elif config_file.suffix.lower() in ['.yaml', '.yml']:
        return yaml.safe_load(content)
    
    else:
        # Try to parse as JSON, then YAML
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                raise ValueError(f"Unable to parse configuration file: {config_path}")


def parse_publish_date(date_value):
    """
    Parse publish date from various formats
    
    Args:
        date_value: Date string, timestamp, or 0 for immediate
    
    Returns:
        datetime object or 0
    """
    if not date_value or date_value == 0 or date_value == "0":
        return 0
    
    if isinstance(date_value, (int, float)):
        return datetime.fromtimestamp(date_value)
    
    # Try different date formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_value), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_value}")


async def upload_from_config(config: dict) -> bool:
    """
    Upload video based on configuration
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if successful, False otherwise
    """
    platform = config.get('platform')
    if not platform:
        raise ValueError("Platform not specified in configuration")
    
    # Extract video info
    video_info = config.get('video', {})
    video_path = video_info.get('path')
    title = video_info.get('title')
    tags = video_info.get('tags', [])
    description = video_info.get('description', title)
    
    if not video_path:
        raise ValueError("Video path not specified")
    
    if not title:
        raise ValueError("Video title not specified")
    
    # Verify video file exists
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Extract account info
    account_info = config.get('account', {})
    account_file = account_info.get('cookie_file')
    
    if not account_file:
        raise ValueError("Account cookie file not specified")
    
    # Extract options
    options = config.get('options', {})
    publish_date = parse_publish_date(options.get('publish_date', 0))
    
    print(f"\n🚀 Uploading to {platform.upper()}...")
    print(f"📹 Video: {video_path}")
    print(f"📝 Title: {title}")
    print(f"🏷️  Tags: {', '.join(tags)}")
    
    try:
        if platform == 'douyin':
            # Setup account
            if not await douyin_setup(account_file, handle=True):
                print("❌ Failed to setup Douyin account")
                return False
            
            # Create video object
            video = DouYinVideo(
                title=title,
                file_path=video_path,
                tags=tags,
                publish_date=publish_date,
                account_file=account_file,
                thumbnail_path=options.get('thumbnail'),
                productLink=options.get('product_link', ''),
                productTitle=options.get('product_title', '')
            )
            await video.main()
        
        elif platform == 'kuaishou':
            # Setup account
            if not await ks_setup(account_file, handle=True):
                print("❌ Failed to setup Kuaishou account")
                return False
            
            # Limit tags to 3
            tags = tags[:3]
            
            # Create video object
            video = KSVideo(
                title=title,
                file_path=video_path,
                tags=tags,
                publish_date=publish_date,
                account_file=account_file
            )
            await video.main()
        
        elif platform == 'tiktok':
            # Setup account
            if not await tiktok_setup(account_file, handle=True):
                print("❌ Failed to setup TikTok account")
                return False
            
            # Create video object
            video = TiktokVideo(
                title=title,
                file_path=video_path,
                tags=tags,
                publish_date=publish_date,
                account_file=account_file
            )
            await video.main()
        
        elif platform == 'tencent':
            # Setup account
            if not await weixin_setup(account_file, handle=True):
                print("❌ Failed to setup Tencent/WeChat account")
                return False
            
            # Create video object
            video = TencentVideo(
                title=title,
                file_path=video_path,
                tags=tags,
                publish_date=publish_date,
                account_file=account_file,
                category=options.get('category')
            )
            await video.main()
        
        elif platform == 'xhs':
            print("⚠️  Xiaohongshu (小红书) upload requires separate signature service")
            print("Please refer to xhs_uploader module for implementation")
            return False
        
        else:
            print(f"❌ Unknown platform: {platform}")
            return False
        
        print(f"\n✅ Successfully uploaded to {platform.upper()}")
        return True
    
    except Exception as e:
        print(f"\n❌ Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def batch_upload(config_list: list) -> dict:
    """
    Upload multiple videos from configuration list
    
    Args:
        config_list: List of configuration dictionaries
    
    Returns:
        Dictionary with success/failure counts
    """
    results = {
        'total': len(config_list),
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for i, config in enumerate(config_list, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(config_list)}")
        print(f"{'='*60}")
        
        try:
            success = await upload_from_config(config)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'index': i,
                    'platform': config.get('platform'),
                    'error': 'Upload failed'
                })
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'index': i,
                'platform': config.get('platform'),
                'error': str(e)
            })
    
    return results


async def main():
    parser = argparse.ArgumentParser(description='Upload video from configuration file')
    parser.add_argument('config', help='Path to configuration file (JSON/YAML)')
    parser.add_argument('--batch', action='store_true', 
                        help='Treat config as batch upload (array of configs)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    if args.batch:
        # Batch upload
        if not isinstance(config, list):
            print("❌ Batch mode requires configuration to be an array")
            return
        
        results = await batch_upload(config)
        
        print(f"\n{'='*60}")
        print("BATCH UPLOAD SUMMARY")
        print(f"{'='*60}")
        print(f"Total: {results['total']}")
        print(f"✅ Success: {results['success']}")
        print(f"❌ Failed: {results['failed']}")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  [{error['index']}] {error['platform']}: {error['error']}")
    
    else:
        # Single upload
        await upload_from_config(config)


if __name__ == '__main__':
    asyncio.run(main())
