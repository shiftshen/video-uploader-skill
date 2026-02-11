#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify platform page loading with anti-detection
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.browser_config import (
    get_platform_specific_config,
    setup_browser_context
)


async def test_platform_page(platform: str):
    """
    Test if platform page loads correctly
    
    Args:
        platform: Platform name (douyin, kuaishou, tiktok, tencent, xhs)
    """
    # Platform URLs
    urls = {
        'douyin': 'https://creator.douyin.com/creator-micro/content/upload',
        'kuaishou': 'https://cp.kuaishou.com/article/publish/video',
        'tiktok': 'https://www.tiktok.com/tiktokstudio/upload',
        'tencent': 'https://channels.weixin.qq.com/platform/post/create',
        'xhs': 'https://creator.xiaohongshu.com/publish/publish',
    }
    
    if platform not in urls:
        print(f"❌ Unknown platform: {platform}")
        print(f"Available platforms: {', '.join(urls.keys())}")
        return False
    
    print(f"\n🔍 Testing {platform.upper()} page load...")
    print(f"URL: {urls[platform]}")
    
    # Get platform-specific config
    config = get_platform_specific_config(platform)
    stealth_js_path = Path(__file__).parent / "utils" / "stealth.min.js"
    
    async with async_playwright() as playwright:
        # Launch browser
        browser_type = getattr(playwright, config['browser'])
        
        launch_options = {
            'headless': True,  # Force headless in sandbox
            'args': config['args'],
        }
        
        print(f"🚀 Launching {config['browser']} browser...")
        browser = await browser_type.launch(**launch_options)
        
        # Create context with anti-detection
        print("🛡️  Setting up anti-detection context...")
        context = await browser.new_context(**config['context_options'])
        context = await setup_browser_context(context, stealth_js_path)
        
        # Create page
        page = await context.new_page()
        
        # Navigate to URL
        print(f"🌐 Navigating to {platform} upload page...")
        try:
            response = await page.goto(urls[platform], wait_until='networkidle', timeout=30000)
            
            if response and response.ok:
                print(f"✅ Page loaded successfully (Status: {response.status})")
            else:
                print(f"⚠️  Page loaded with status: {response.status if response else 'unknown'}")
            
            # Wait a bit to see the page
            print("⏳ Waiting 5 seconds to observe page...")
            await asyncio.sleep(5)
            
            # Take screenshot
            screenshot_path = Path(__file__).parent.parent / f"test_{platform}_page.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Check for common anti-bot indicators
            print("\n🔍 Checking for anti-bot indicators...")
            
            # Check if redirected to login
            current_url = page.url
            if 'login' in current_url.lower():
                print("⚠️  Redirected to login page (expected without cookies)")
            else:
                print(f"✅ Current URL: {current_url}")
            
            # Check for captcha
            captcha_selectors = [
                'text=验证',
                'text=Verify',
                'text=captcha',
                '[id*="captcha"]',
                '[class*="captcha"]',
            ]
            
            captcha_found = False
            for selector in captcha_selectors:
                if await page.locator(selector).count() > 0:
                    print(f"⚠️  Captcha detected: {selector}")
                    captcha_found = True
                    break
            
            if not captcha_found:
                print("✅ No captcha detected")
            
            # Check for block messages
            block_selectors = [
                'text=访问被拒绝',
                'text=Access Denied',
                'text=blocked',
                'text=forbidden',
            ]
            
            blocked = False
            for selector in block_selectors:
                if await page.locator(selector).count() > 0:
                    print(f"❌ Access blocked: {selector}")
                    blocked = True
                    break
            
            if not blocked:
                print("✅ No block message detected")
            
            # Platform-specific checks
            if platform == 'douyin':
                upload_button = await page.locator('div[class*="container"] input[type="file"]').count()
                if upload_button > 0:
                    print("✅ Upload button found (logged in)")
                else:
                    print("⚠️  Upload button not found (need login)")
            
            elif platform == 'tiktok':
                upload_button = await page.locator('button:has-text("Select video")').count()
                if upload_button > 0:
                    print("✅ Upload button found (logged in)")
                else:
                    print("⚠️  Upload button not found (need login)")
            
            print(f"\n✅ {platform.upper()} page test completed")
            return True
            
        except Exception as e:
            print(f"❌ Error loading page: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            await context.close()
            await browser.close()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_page_load.py <platform>")
        print("Platforms: douyin, kuaishou, tiktok, tencent, xhs")
        return
    
    platform = sys.argv[1].lower()
    await test_platform_page(platform)


if __name__ == '__main__':
    asyncio.run(main())
