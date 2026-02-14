#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xiaohongshu (小红书) Uploader using browser automation
"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
from conf import LOCAL_CHROME_PATH, BASE_DIR


class XiaohongshuVideo:
    def __init__(self, title, file_path, tags, publish_date=0, account_file=None):
        self.title = title
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.local_executable_path = LOCAL_CHROME_PATH
        
    async def setup_browser(self, playwright):
        """Setup browser with stealth - use persistent context to save login state"""
        stealth_js_path = BASE_DIR / "utils/stealth.min.js"
        
        # Use persistent user data dir to save login state
        user_data_dir = BASE_DIR / "cookies/xhs_uploader/browser_data"
        
        if self.local_executable_path:
            # Launch with persistent context - this keeps cookies and login state
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                executable_path=self.local_executable_path,
                args=['--disable-blink-features=AutomationControlled']
            )
        else:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
        
        # Add stealth script
        await context.add_init_script(path=stealth_js_path)
        
        # Get the default page
        page = context.pages[0] if context.pages else await context.new_page()
        
        return context, page
    
    async def upload(self, playwright):
        """Upload video using browser"""
        context, page = await self.setup_browser(playwright)
        
        # Go to creator upload page
        await page.goto('https://creator.xiaohongshu.com/publish/publish?source=official')
        await page.wait_for_timeout(5000)
        
        # Check if login required
        if 'login' in page.url:
            print("请在浏览器中登录账号...（登录后会保存状态，下次不需要再登录）")
            await page.wait_for_timeout(120000)  # Wait for manual login
            await page.wait_for_timeout(5000)
        
        # Wait for page to load
        await page.wait_for_timeout(3000)
        
        # Find file input - it might be hidden so we can't use wait_for_selector
        print("查找文件上传输入框...")
        file_input = await page.query_selector('input[type="file"]')
        
        if file_input:
            print("找到文件上传输入框 (hidden)")
            # Set files even if hidden - Playwright can handle this
            await file_input.set_input_files(self.file_path)
            print(f"已选择视频: {self.file_path}")
        else:
            # Try clicking upload button first
            print("尝试点击上传按钮...")
            upload_buttons = await page.query_selector_all('button')
            for btn in upload_buttons:
                text = await btn.inner_text()
                if '上传' in text and '视频' in text:
                    print(f"点击上传按钮: {text}")
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    file_input = await page.query_selector('input[type="file"]')
                    if file_input:
                        await file_input.set_input_files(self.file_path)
                        print(f"已选择视频: {self.file_path}")
                        break
            else:
                print("未找到上传入口!")
                await browser.close()
                return False
        
        # Wait for video to upload - look for title input which appears after upload
        print("等待视频上传完成...")
        await page.wait_for_timeout(15000)
        
        # Now fill in title and description - they should appear after upload
        print("填写标题...")
        
        # Try multiple selectors for title
        title_filled = False
        title_selectors = [
            'input[placeholder*="标题"]',
            'input[placeholder*="标题"]',
            'input[class*="title"]',
            'input[class*="Title"]',
            'input'
        ]
        
        for selector in title_selectors:
            try:
                inputs = await page.query_selector_all(selector)
                for inp in inputs:
                    placeholder = await inp.get_attribute('placeholder') or ''
                    if '标题' in placeholder:
                        await inp.fill(self.title)
                        print(f"标题已填写: {self.title}")
                        title_filled = True
                        break
                if title_filled:
                    break
            except:
                pass
        
        # Fill description - look for textareas or editable divs
        print("填写正文和话题...")
        desc = self.title
        if self.tags:
            for tag in self.tags:
                desc += f" #{tag}"
        
        desc_filled = False
        desc_selectors = [
            'textarea[placeholder*="正文"]',
            'textarea[placeholder*="描述"]',
            'textarea[placeholder*="内容"]',
            'div[contenteditable="true"]',
            'textarea'
        ]
        
        for selector in desc_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    placeholder = await el.get_attribute('placeholder') or ''
                    # Skip login-related fields
                    if '登录' in placeholder or '手机' in placeholder or '验证码' in placeholder:
                        continue
                    text = await el.inner_text()
                    if len(text) < 1000:  # Likely a content field
                        await el.fill(desc)
                        print(f"正文已填写: {desc[:50]}...")
                        desc_filled = True
                        break
                if desc_filled:
                    break
            except:
                pass
        
        # Wait a bit for fields to settle
        await page.wait_for_timeout(2000)
        
        # Save cookies
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        os.makedirs(os.path.dirname(self.account_file), exist_ok=True)
        with open(self.account_file, 'w') as f:
            json.dump(cookie_dict, f, indent=2)
        print("Cookie saved!")
        
        # Click publish button
        print("点击发布按钮...")
        publish_buttons = await page.query_selector_all('button')
        for btn in publish_buttons:
            text = await btn.inner_text()
            if '发布' in text or '发表' in text:
                print(f"点击发布: {text}")
                await btn.click()
                break
        
        await page.wait_for_timeout(5000)
        print("上传流程完成!")
        
        # Don't close context - keep it open to preserve login state
        # await browser.close()
        return True
    
    async def main(self):
        """Main entry point"""
        async with async_playwright() as playwright:
            await self.upload(playwright)


async def xhs_setup(account_file, handle=False):
    """Setup and verify Xiaohongshu account"""
    if not account_file:
        return False
    
    # Check if cookie file exists
    if not os.path.exists(account_file):
        print(f"Warning: Account file not found: {account_file}")
        if handle:
            print("Please login via browser when prompted...")
        return False
    
    # Verify cookie has required fields
    with open(account_file, 'r') as f:
        cookies = json.load(f)
    
    if 'a1' not in cookies:
        print("Warning: Cookie missing 'a1' field")
        return False
    
    print(f"[+] Xiaohongshu account configured")
    return True


async def main():
    """Test upload"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=True)
    parser.add_argument('--video', required=True)
    parser.add_argument('--tags', default='')
    parser.add_argument('--account', default='cookies/xhs_uploader/cookie.json')
    args = parser.parse_args()
    
    tags = args.tags.split(',') if args.tags else []
    
    video = XiaohongshuVideo(
        title=args.title,
        file_path=args.video,
        tags=tags,
        account_file=args.account
    )
    await video.main()


if __name__ == '__main__':
    asyncio.run(main())
