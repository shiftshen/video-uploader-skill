# -*- coding: utf-8 -*-
import re
from datetime import datetime

from playwright.async_api import Playwright, async_playwright
import os
import asyncio
from uploader.tk_uploader.tk_config import Tk_Locator
from utils.base_social_media import set_init_script
from utils.files_times import get_absolute_path
from utils.log import tiktok_logger


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, channel="chrome")
        context = await browser.new_context(
        storage_state=account_file,
        locale="en-US",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        bypass_csp=True
    )
        context = await set_init_script(context)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://www.tiktok.com/tiktokstudio/upload?lang=en")
        await page.wait_for_load_state('networkidle')
        try:
            # 选择所有的 select 元素
            select_elements = await page.query_selector_all('select')
            for element in select_elements:
                class_name = await element.get_attribute('class')
                # 使用正则表达式匹配特定模式的 class 名称
                if re.match(r'tiktok-.*-SelectFormContainer.*', class_name):
                    tiktok_logger.error("[+] cookie expired")
                    return False
            tiktok_logger.success("[+] cookie valid")
            return True
        except:
            tiktok_logger.success("[+] cookie valid")
            return True


async def tiktok_setup(account_file, handle=False):
    account_file = get_absolute_path(account_file, "tk_uploader")
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            return False
        tiktok_logger.info('[+] cookie file is not existed or expired. Now open the browser auto. Please login with your way(gmail phone, whatever, the cookie file will generated after login')
        await get_tiktok_cookie(account_file)
    return True


async def get_tiktok_cookie(account_file):
    import asyncio
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context(
            locale="en-US",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            bypass_csp=True
        )
        context = await set_init_script(context)
        page = await context.new_page()
        
        print("=== TikTok 登录 ===")
        print("请在手机上扫码登录...")
        await page.goto("https://www.tiktok.com/login?lang=en")
        
        # 等待登录成功（最多120秒）
        try:
            await page.wait_for_url("https://www.tiktok.com/**", timeout=120000)
            # 检测是否还在登录页
            if "/login" not in page.url:
                print("✅ 检测到登录成功！")
                await asyncio.sleep(2)  # 等待cookie稳定
                await context.storage_state(path=account_file)
                print(f"✅ Cookie已保存: {account_file}")
                return
        except:
            pass
        
        # 如果URL检测失败，尝试检测登录后元素
        print("等待扫码...")
        for i in range(120):
            await asyncio.sleep(1)
            try:
                # 检查是否登录成功（通过检查页面元素）
                creator_btn = await page.locator('a[href*="creator"]').count()
                if creator_btn > 0 or "/login" not in page.url:
                    print("✅ 登录成功！")
                    await context.storage_state(path=account_file)
                    print(f"✅ Cookie已保存: {account_file}")
                    return
            except:
                pass
            if i % 10 == 0:
                print(f"  等待中... {i}秒")
        
        print("⚠️ 登录超时，请重试")
        await browser.close()


class TiktokVideo(object):
    def __init__(self, title, file_path, tags, publish_date, account_file):
        self.title = title
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.locator_base = None


    async def set_schedule_time(self, page, publish_date):
        schedule_input_element = self.locator_base.get_by_label('Schedule')
        await schedule_input_element.wait_for(state='visible')  # 确保按钮可见

        await schedule_input_element.click()
        scheduled_picker = self.locator_base.locator('div.scheduled-picker')
        await scheduled_picker.locator('div.TUXInputBox').nth(1).click()

        calendar_month = await self.locator_base.locator('div.calendar-wrapper span.month-title').inner_text()

        n_calendar_month = datetime.strptime(calendar_month, '%B').month

        schedule_month = publish_date.month

        if n_calendar_month != schedule_month:
            if n_calendar_month < schedule_month:
                arrow = self.locator_base.locator('div.calendar-wrapper span.arrow').nth(-1)
            else:
                arrow = self.locator_base.locator('div.calendar-wrapper span.arrow').nth(0)
            await arrow.click()

        # day set
        valid_days_locator = self.locator_base.locator(
            'div.calendar-wrapper span.day.valid')
        valid_days = await valid_days_locator.count()
        for i in range(valid_days):
            day_element = valid_days_locator.nth(i)
            text = await day_element.inner_text()
            if text.strip() == str(publish_date.day):
                await day_element.click()
                break
        # time set
        await scheduled_picker.locator('div.TUXInputBox').nth(0).click()

        hour_str = publish_date.strftime("%H")
        correct_minute = int(publish_date.minute / 5)
        minute_str = f"{correct_minute:02d}"

        hour_selector = f"span.tiktok-timepicker-left:has-text('{hour_str}')"
        minute_selector = f"span.tiktok-timepicker-right:has-text('{minute_str}')"

        # pick hour first
        await self.locator_base.locator(hour_selector).click()
        # click time button again
        # 等待某个特定的元素出现或状态变化，表明UI已更新
        await page.wait_for_timeout(1000)  # 等待500毫秒
        await scheduled_picker.locator('div.TUXInputBox').nth(0).click()
        # pick minutes after
        await self.locator_base.locator(minute_selector).click()

        # click title to remove the focus.
        await self.locator_base.locator("h1:has-text('Upload video')").click()

    async def handle_upload_error(self, page):
        tiktok_logger.info("video upload error retrying.")
        select_file_button = self.locator_base.locator('button[aria-label="Select file"]')
        async with page.expect_file_chooser() as fc_info:
            await select_file_button.click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context(
            storage_state=f"{self.account_file}",
            locale="en-US",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            bypass_csp=True
        )
        context = await set_init_script(context)
        page = await context.new_page()

        await page.goto("https://www.tiktok.com/tiktokstudio/upload")
        tiktok_logger.info(f'[+]Uploading-------{self.title}.mp4')

        # Wait for page load
        await asyncio.sleep(5)

        # Set locator_base to page for simpler approach
        self.locator_base = page

        # Direct file input approach (more reliable)
        try:
            file_input = page.locator('input[type="file"]').first
            if await file_input.count() > 0:
                tiktok_logger.info("Found file input, uploading directly...")
                await file_input.set_input_files(self.file_path)
            else:
                # Fallback
                upload_btn = page.locator('button:has-text("Select video")').first
                if await upload_btn.count() > 0:
                    async with page.expect_file_chooser() as fc:
                        await upload_btn.click()
                    file_chooser = await fc.value
                    await file_chooser.set_files(self.file_path)
        except Exception as e:
            tiktok_logger.error(f"Upload error: {e}")

        # Wait for upload
        tiktok_logger.info("Waiting for upload to complete...")
        await asyncio.sleep(30)

        await self.add_title_tags(page)

        # Wait for publish button
        try:
            await page.locator('button:has-text("Post"):visible').wait_for(timeout=60000)
            tiktok_logger.info("Video uploaded successfully!")
        except Exception as e:
            tiktok_logger.warning(f"Could not find Post button: {e}")

        await self.click_publish(page)

        await context.storage_state(path=f"{self.account_file}")
        tiktok_logger.info('  [-] update cookie!')
        await asyncio.sleep(2)
        await context.close()
        await browser.close()

    async def add_title_tags(self, page):
        
        # Close any overlay or modal
        try:
            close_buttons = [
                'button[aria-label="Close"]',
                'button[data-test-id="close-button"]',
                'div[role="button"]:has-text("Skip")',
                'button:has-text("Skip")',
                'button:has-text("Close")',
            ]
            for selector in close_buttons:
                btn = page.locator(selector).first
                if await btn.count() > 0:
                    try:
                        await btn.click(timeout=2000)
                        await asyncio.sleep(1)
                    except:
                        pass
        except:
            pass
        
        # Press Escape to close any modal
        await page.keyboard.press("Escape")
        await asyncio.sleep(1)

        editor_locator = self.locator_base.locator('div.public-DraftEditor-content')
        # Use force click to bypass overlay
        await editor_locator.click(force=True, timeout=10000)
        
        await page.keyboard.press("End")

        await page.keyboard.press("Control+A")

        await page.keyboard.press("Delete")

        await page.keyboard.press("End")

        await page.wait_for_timeout(1000)  # 等待1秒

        await page.keyboard.insert_text(self.title)
        await page.wait_for_timeout(1000)  # 等待1秒
        await page.keyboard.press("End")

        await page.keyboard.press("Enter")

        # tag part
        for index, tag in enumerate(self.tags, start=1):
            tiktok_logger.info("Setting the %s tag" % index)
            await page.keyboard.press("End")
            await page.wait_for_timeout(1000)  # 等待1秒
            await page.keyboard.insert_text("#" + tag + " ")
            await page.keyboard.press("Space")
            await page.wait_for_timeout(1000)  # 等待1秒

            await page.keyboard.press("Backspace")
            await page.keyboard.press("End")

    async def click_publish(self, page):
        success_flag_div = '#\\:r9\\:'
        while True:
            try:
                publish_button = self.locator_base.locator('div.btn-post')
                if await publish_button.count():
                    await publish_button.click()

                await self.locator_base.locator(success_flag_div).wait_for(state="visible", timeout=3000)
                tiktok_logger.success("  [-] video published success")
                break
            except Exception as e:
                if await self.locator_base.locator(success_flag_div).count():
                    tiktok_logger.success("  [-]video published success")
                    break
                else:
                    tiktok_logger.exception(f"  [-] Exception: {e}")
                    tiktok_logger.info("  [-] video publishing")
                    await page.screenshot(full_page=True)
                    await asyncio.sleep(0.5)

    async def detect_upload_status(self, page):
        while True:
            try:
                if await self.locator_base.locator('div.btn-post > button').get_attribute("disabled") is None:
                    tiktok_logger.info("  [-]video uploaded.")
                    break
                else:
                    tiktok_logger.info("  [-] video uploading...")
                    await asyncio.sleep(2)
                    if await self.locator_base.locator('button[aria-label="Select file"]').count():
                        tiktok_logger.info("  [-] found some error while uploading now retry...")
                        await self.handle_upload_error(page)
            except:
                tiktok_logger.info("  [-] video uploading...")
                await asyncio.sleep(2)

    async def choose_base_locator(self, page):
        # await page.wait_for_selector('div.upload-container')
        if await page.locator('iframe[data-tt="Upload_index_iframe"]').count():
            self.locator_base = self.locator_base
        else:
            self.locator_base = page.locator(Tk_Locator.default) 

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

