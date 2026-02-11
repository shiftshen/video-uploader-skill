#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate upload configuration from video file and AI-powered content analysis
This script helps OpenClaw/AI generate all necessary fields for video upload
"""
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import re


def sanitize_filename_to_title(filename: str) -> str:
    """
    Convert filename to readable title
    
    Args:
        filename: Video filename
    
    Returns:
        Cleaned title string
    """
    # Remove extension
    title = Path(filename).stem
    
    # Replace separators with spaces
    title = re.sub(r'[_\-\.]', ' ', title)
    
    # Remove special characters except Chinese
    title = re.sub(r'[^\w\s\u4e00-\u9fff]', '', title)
    
    # Capitalize first letter of each word (for English)
    title = ' '.join(word.capitalize() if word.isascii() else word for word in title.split())
    
    # Remove extra spaces
    title = ' '.join(title.split())
    
    return title


def extract_tags_from_title(title: str, max_tags: int = 10) -> list:
    """
    Extract potential tags from title
    
    Args:
        title: Video title
        max_tags: Maximum number of tags
    
    Returns:
        List of tags
    """
    # Common stop words to remove
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
        '这', '个', '们', '中', '来', '上', '大', '为', '到', '说', '要'
    }
    
    # Split title into words
    words = re.findall(r'[\w\u4e00-\u9fff]+', title.lower())
    
    # Filter out stop words and short words
    tags = [word for word in words if word not in stop_words and len(word) > 1]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags[:max_tags]


def format_short_title_for_tencent(title: str) -> str:
    """
    Format title for Tencent Video short title requirements
    6-16 characters, limited special characters
    
    Args:
        title: Original title
    
    Returns:
        Formatted short title
    """
    # Allowed special characters
    allowed_special = "《》"":+?%°"
    
    # Remove disallowed special characters
    filtered_chars = []
    for char in title:
        if char.isalnum() or char in allowed_special:
            filtered_chars.append(char)
        elif char == ',':
            filtered_chars.append(' ')
    
    short_title = ''.join(filtered_chars).strip()
    
    # Adjust length
    if len(short_title) > 16:
        short_title = short_title[:16]
    elif len(short_title) < 6:
        # Pad with spaces if too short
        short_title += ' ' * (6 - len(short_title))
    
    return short_title


def generate_schedule_time(days_ahead: int = 1, hour: int = 18, minute: int = 0) -> str:
    """
    Generate schedule time for future publishing
    
    Args:
        days_ahead: Number of days in the future
        hour: Hour of day (0-23)
        minute: Minute of hour (0-59)
    
    Returns:
        Formatted datetime string
    """
    schedule_time = datetime.now() + timedelta(days=days_ahead)
    schedule_time = schedule_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return schedule_time.strftime("%Y-%m-%d %H:%M:%S")


def generate_config(
    platform: str,
    video_path: str,
    title: str = None,
    tags: list = None,
    description: str = None,
    account_file: str = None,
    publish_date: str = None,
    output_format: str = 'json',
    **kwargs
) -> dict:
    """
    Generate complete upload configuration
    
    Args:
        platform: Target platform
        video_path: Path to video file
        title: Video title (auto-generated if not provided)
        tags: List of tags (auto-generated if not provided)
        description: Video description (auto-generated if not provided)
        account_file: Path to cookie file
        publish_date: Schedule time or None for immediate
        output_format: Output format (json/yaml/command)
        **kwargs: Additional platform-specific options
    
    Returns:
        Configuration dictionary
    """
    # Verify video file exists
    video_path = Path(video_path).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Auto-generate title if not provided
    if not title:
        title = sanitize_filename_to_title(video_path.name)
    
    # Auto-generate tags if not provided
    if not tags:
        tags = extract_tags_from_title(title)
    
    # Auto-generate description if not provided
    if not description:
        description = title
    
    # Default account file path
    if not account_file:
        account_file = f"/home/ubuntu/cookies/{platform}_account.json"
    
    # Base configuration
    config = {
        'platform': platform,
        'video': {
            'path': str(video_path),
            'title': title,
            'description': description,
            'tags': tags
        },
        'account': {
            'cookie_file': account_file
        },
        'options': {}
    }
    
    # Add publish date if specified
    if publish_date:
        config['options']['publish_date'] = publish_date
    
    # Platform-specific options
    if platform == 'douyin':
        # Limit title to 30 characters
        config['video']['title'] = title[:30]
        
        if kwargs.get('thumbnail'):
            config['options']['thumbnail'] = kwargs['thumbnail']
        if kwargs.get('product_link'):
            config['options']['product_link'] = kwargs['product_link']
        if kwargs.get('product_title'):
            config['options']['product_title'] = kwargs['product_title']
    
    elif platform == 'kuaishou':
        # Limit tags to 3
        config['video']['tags'] = tags[:3]
    
    elif platform == 'tencent':
        if kwargs.get('category'):
            config['options']['category'] = kwargs['category']
        if kwargs.get('is_original'):
            config['options']['is_original'] = kwargs['is_original']
        
        # Generate short title
        config['options']['short_title'] = format_short_title_for_tencent(title)
    
    elif platform == 'tiktok':
        if kwargs.get('privacy'):
            config['options']['privacy'] = kwargs['privacy']
        if kwargs.get('allow_comments') is not None:
            config['options']['allow_comments'] = kwargs['allow_comments']
        if kwargs.get('allow_duet') is not None:
            config['options']['allow_duet'] = kwargs['allow_duet']
    
    elif platform == 'xhs':
        if kwargs.get('cover_path'):
            config['options']['cover_path'] = kwargs['cover_path']
        if kwargs.get('location'):
            config['options']['location'] = kwargs['location']
    
    return config


def config_to_command(config: dict) -> str:
    """
    Convert configuration to command-line format
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Command string
    """
    cmd_parts = ['python upload_video.py']
    
    # Platform
    cmd_parts.append(f"--platform {config['platform']}")
    
    # Video info
    cmd_parts.append(f"--video \"{config['video']['path']}\"")
    cmd_parts.append(f"--title \"{config['video']['title']}\"")
    cmd_parts.append(f"--tags \"{','.join(config['video']['tags'])}\"")
    
    # Account
    cmd_parts.append(f"--account \"{config['account']['cookie_file']}\"")
    
    # Options
    for key, value in config.get('options', {}).items():
        key_formatted = key.replace('_', '-')
        if isinstance(value, bool):
            if value:
                cmd_parts.append(f"--{key_formatted}")
        else:
            cmd_parts.append(f"--{key_formatted} \"{value}\"")
    
    return ' \\\n  '.join(cmd_parts)


def main():
    parser = argparse.ArgumentParser(description='Generate video upload configuration')
    parser.add_argument('--platform', required=True, 
                        choices=['douyin', 'kuaishou', 'tiktok', 'tencent', 'xhs'],
                        help='Target platform')
    parser.add_argument('--video', required=True, help='Path to video file')
    parser.add_argument('--title', help='Video title (auto-generated if not provided)')
    parser.add_argument('--tags', help='Comma-separated tags (auto-generated if not provided)')
    parser.add_argument('--description', help='Video description')
    parser.add_argument('--account', help='Path to account cookie file')
    parser.add_argument('--schedule-days', type=int, default=0, 
                        help='Schedule N days ahead (0 for immediate)')
    parser.add_argument('--schedule-hour', type=int, default=18,
                        help='Schedule hour (0-23)')
    parser.add_argument('--output', choices=['json', 'yaml', 'command'], default='json',
                        help='Output format')
    parser.add_argument('--output-file', help='Save to file instead of stdout')
    
    # Platform-specific options
    parser.add_argument('--thumbnail', help='Thumbnail path (Douyin)')
    parser.add_argument('--product-link', help='Product link (Douyin)')
    parser.add_argument('--product-title', help='Product title (Douyin)')
    parser.add_argument('--category', help='Video category (Tencent)')
    parser.add_argument('--is-original', action='store_true', help='Declare original (Tencent)')
    parser.add_argument('--cover', help='Cover image path (XHS)')
    parser.add_argument('--location', help='Location (XHS)')
    
    args = parser.parse_args()
    
    # Parse tags if provided
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]
    
    # Generate schedule time if specified
    publish_date = None
    if args.schedule_days > 0:
        publish_date = generate_schedule_time(args.schedule_days, args.schedule_hour)
    
    # Generate configuration
    config = generate_config(
        platform=args.platform,
        video_path=args.video,
        title=args.title,
        tags=tags,
        description=args.description,
        account_file=args.account,
        publish_date=publish_date,
        output_format=args.output,
        thumbnail=args.thumbnail,
        product_link=args.product_link,
        product_title=args.product_title,
        category=args.category,
        is_original=args.is_original,
        cover_path=args.cover,
        location=args.location
    )
    
    # Format output
    if args.output == 'json':
        output = json.dumps(config, indent=2, ensure_ascii=False)
    elif args.output == 'yaml':
        output = yaml.dump(config, allow_unicode=True, default_flow_style=False)
    elif args.output == 'command':
        output = config_to_command(config)
    
    # Save or print
    if args.output_file:
        Path(args.output_file).write_text(output, encoding='utf-8')
        print(f"✅ Configuration saved to: {args.output_file}")
    else:
        print(output)


if __name__ == '__main__':
    main()
