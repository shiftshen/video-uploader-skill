# -*- coding: utf-8 -*-
from datetime import datetime

from playwright.async_api import Playwright, async_playwright, Page, TimeoutError as PlaywrightTimeoutError
import os
import asyncio

from conf import LOCAL_CHROME_PATH
from utils.base_social_media import set_init_script
from utils.log import douyin_logger


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        if LOCAL_CHROME_PATH:
            browser = await playwright.chromium.launch(headless=True, channel="chrome", executable_path=LOCAL_CHROME_PATH)
        else:
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
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        try:
            await page.wait_for_url("https://creator.douyin.com/creator-micro/content/upload", timeout=5000)
        except:
            print("[+] 等待5秒 cookie 失效")
            await context.close()
            await browser.close()
            return False
        # 2024.06.17 抖音创作者中心改版
        if await page.get_by_text('手机号登录').count() or await page.get_by_text('扫码登录').count():
            print("[+] 等待5秒 cookie 失效")
            return False
        else:
            print("[+] cookie 有效")
            return True


async def douyin_setup(account_file, handle=False):
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            # Todo alert message
            return False
        douyin_logger.info('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
        await douyin_cookie_gen(account_file)
    return True


async def douyin_cookie_gen(account_file):
    import asyncio
    
    async with async_playwright() as playwright:
        if LOCAL_CHROME_PATH:
            browser = await playwright.chromium.launch(channel="chrome", headless=False, executable_path=LOCAL_CHROME_PATH)
        else:
            browser = await playwright.chromium.launch(channel="chrome", headless=False)
        
        context = await browser.new_context(
            locale="en-US",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            bypass_csp=True
        )
        context = await set_init_script(context)
        page = await context.new_page()
        
        print("=== 抖音登录 ===")
        print("请在手机上扫码登录...")
        await page.goto("https://creator.douyin.com/")
        
        # 等待登录成功（最多120秒）
        login_success = False
        for i in range(120):
            await asyncio.sleep(1)
            current_url = page.url
            
            # 检测登录成功 - URL变化
            if "/creator-micro" in current_url or "/content/manage" in current_url:
                print("✅ 检测到登录成功！(已跳转到创作者中心)")
                login_success = True
                break
            
            # 检测页面元素
            if await page.locator('text=发布作品').count() > 0:
                print("✅ 检测到登录成功！(发现发布作品)")
                login_success = True
                break
            
            if await page.locator('text=视频管理').count() > 0:
                print("✅ 检测到登录成功！(发现视频管理)")
                login_success = True
                break
            
            if i % 20 == 0:
                print(f"  等待中... {i}秒")
        
        if login_success:
            await asyncio.sleep(3)
            await context.storage_state(path=account_file)
            print(f"✅ Cookie已保存: {account_file}")
        else:
            print("⚠️ 登录超时，请重试")
        
        await browser.close()


class DouYinVideo(object):
    def __init__(self, title, file_path, tags, publish_date: datetime, account_file, thumbnail_path=None, productLink='', productTitle='', ai_generated=False):
        self.title = title  # 视频标题
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.date_format = '%Y年%m月%d日 %H:%M'
        self.local_executable_path = LOCAL_CHROME_PATH
        self.thumbnail_path = thumbnail_path
        self.productLink = productLink
        self.productTitle = productTitle
        self.ai_generated = ai_generated  # AI 生成内容标记

    async def set_schedule_time_douyin(self, page, publish_date):
        # 选择包含特定文本内容的 label 元素
        label_element = page.locator("[class^='radio']:has-text('定时发布')")
        # 在选中的 label 元素下点击 checkbox
        await label_element.click()
        await asyncio.sleep(1)
        publish_date_hour = publish_date.strftime("%Y-%m-%d %H:%M")

        await asyncio.sleep(1)
        await page.locator('.semi-input[placeholder="日期和时间"]').click()
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date_hour))
        await page.keyboard.press("Enter")

        await asyncio.sleep(1)

    async def handle_upload_error(self, page):
        douyin_logger.info('视频出错了，重新上传中')
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # 使用 Chromium 浏览器启动一个浏览器实例
        if self.local_executable_path:
            browser = await playwright.chromium.launch(headless=False, channel="chrome", executable_path=self.local_executable_path)
        else:
            browser = await playwright.chromium.launch(headless=False, channel="chrome")
        # 创建一个浏览器上下文，使用指定的 cookie 文件
        context = await browser.new_context(
        storage_state=f"{self.account_file}",
        locale="en-US",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        bypass_csp=True
    )
        context = await set_init_script(context)

        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        douyin_logger.info(f'[+]正在上传-------{self.title}.mp4')
        # 等待页面跳转到指定的 URL，没进入，则自动等待到超时
        douyin_logger.info(f'[-] 正在打开主页...')
        await page.wait_for_url("https://creator.douyin.com/creator-micro/content/upload")
        # 点击 "上传视频" 按钮
        await page.locator("div[class^='container'] input").set_input_files(self.file_path)

        # 等待页面跳转到指定的 URL 2025.01.08修改在原有基础上兼容两种页面
        while True:
            try:
                # 尝试等待第一个 URL
                await page.wait_for_url(
                    "https://creator.douyin.com/creator-micro/content/publish?enter_from=publish_page", timeout=3000)
                douyin_logger.info("[+] 成功进入version_1发布页面!")
                break  # 成功进入页面后跳出循环
            except Exception:
                try:
                    # 如果第一个 URL 超时，再尝试等待第二个 URL
                    await page.wait_for_url(
                        "https://creator.douyin.com/creator-micro/content/post/video?enter_from=publish_page",
                        timeout=3000)
                    douyin_logger.info("[+] 成功进入version_2发布页面!")

                    break  # 成功进入页面后跳出循环
                except:
                    print("  [-] 超时未进入视频发布页面，重新尝试...")
                    await asyncio.sleep(0.5)  # 等待 0.5 秒后重新尝试
        # 填充标题和话题
        # 检查是否存在包含输入框的元素
        # 这里为了避免页面变化，故使用相对位置定位：作品标题父级右侧第一个元素的input子元素
        await asyncio.sleep(1)
        
        # 关闭可能存在的弹窗
        await self.close_popups(page)
        douyin_logger.info('  [-] 已检查并关闭弹窗')
        
        # 等待页面稳定
        await asyncio.sleep(2)
        
        # 再次关闭弹窗（可能有多层）
        await self.close_popups(page)
        await asyncio.sleep(1)
        
        # 调试：截图查看当前页面状态
        try:
            screenshot_path = f"/tmp/douyin_debug_{int(asyncio.get_event_loop().time())}.png"
            await page.screenshot(path=screenshot_path, full_page=False)
            douyin_logger.info(f'  [-] 调试截图已保存: {screenshot_path}')
        except:
            pass
        
        douyin_logger.info(f'  [-] 正在填充标题和作品简介...')
        
        # 先尝试找到任何可编辑区域
        all_editable = page.locator('[contenteditable="true"], input[type="text"], textarea')
        editable_count = await all_editable.count()
        douyin_logger.info(f'  [-] 找到 {editable_count} 个可编辑元素')
        
        title_selectors = [
            "input.semi-input[placeholder*='作品标题']",
            "input.semi-input[placeholder*='填写作品标题']",
            "input[placeholder*='作品标题']",
            ".editor-comp-publish-container-d4oeQI input.semi-input",
            "input.semi-input",
            'input[type="text"]',
        ]
        title_container = await self.locate_first_visible(page, title_selectors, timeout=10000)
        if title_container:
            await title_container.fill(self.title[:30])
            douyin_logger.info('  [-] 标题填充成功 (input)')
        else:
            # 备选方案：使用键盘输入
            try:
                titlecontainer = page.locator(".notranslate, [contenteditable='true']").first
                if await titlecontainer.count() > 0:
                    await titlecontainer.click(timeout=3000)
                    await page.keyboard.press("Control+KeyA")
                    await page.keyboard.press("Delete")
                    await page.keyboard.type(self.title[:30])
                    douyin_logger.info('  [-] 标题填充成功 (contenteditable)')
                else:
                    douyin_logger.warning('  [-] 未找到标题输入框，跳过标题填充')
            except Exception as e:
                douyin_logger.warning(f'  [-] 标题填充失败: {e}，继续...')

        description_selectors = [
            ".editor-kit-editor-container .zone-container.editor[contenteditable='true']",
            ".zone-container.editor[contenteditable='true']",
            ".editor-kit-editor-container [contenteditable='true']",
            ".editor-comp-publish-container-d4oeQI [contenteditable='true']",
            "[contenteditable='true'][data-placeholder*='作品简介']",
            "[contenteditable='true'][data-placeholder*='正文']",
            "[contenteditable='true']",
            "textarea",
        ]
        description_editor = await self.locate_first_visible(page, description_selectors, timeout=10000)
        if description_editor is None:
            douyin_logger.warning('  [-] 未找到描述编辑器，尝试使用第一个可编辑元素')
            # 尝试使用第一个可编辑元素
            if editable_count > 0:
                description_editor = all_editable.first
            else:
                douyin_logger.error('  [-] 没有找到任何可编辑元素')
                # 不抛出异常，继续尝试
        else:
            await description_editor.click()
            try:
                await description_editor.press("Control+KeyA")
                await description_editor.press("Delete")
            except Exception:
                pass

        if description_editor:
            if self.title:
                await description_editor.type(self.title)
                await description_editor.type("\n")

            for index, tag in enumerate(self.tags, start=1):
                await description_editor.type(f"#{tag} ")
                await page.wait_for_timeout(200)
            await page.wait_for_timeout(500)
            douyin_logger.info(f'总共添加{len(self.tags)}个话题')
        while True:
            # 判断重新上传按钮是否存在，如果不存在，代表视频正在上传，则等待
            try:
                #  新版：定位重新上传
                number = await page.locator('[class^="long-card"] div:has-text("重新上传")').count()
                if number > 0:
                    douyin_logger.success("  [-]视频上传完毕")
                    break
                else:
                    douyin_logger.info("  [-] 正在上传视频中...")
                    await asyncio.sleep(1)  # 优化：减少等待时间

                    if await page.locator('div.progress-div > div:has-text("上传失败")').count():
                        douyin_logger.error("  [-] 发现上传出错了... 准备重试")
                        await self.handle_upload_error(page)
            except:
                douyin_logger.info("  [-] 正在上传视频中...")
                await asyncio.sleep(1)

        if self.productLink and self.productTitle:
            douyin_logger.info(f'  [-] 正在设置商品链接...')
            await self.set_product_link(page, self.productLink, self.productTitle)
            douyin_logger.info(f'  [+] 完成设置商品链接...')
        
        #上传视频封面
        await self.set_thumbnail(page, self.thumbnail_path)
        douyin_logger.info('  [-] 封面设置完成')

        # 更换可见元素
        await self.set_location(page, "")

        # 设置 AI 生成内容标记
        if self.ai_generated:
            await self.set_ai_generated(page)


        # 頭條/西瓜
        third_part_element = '[class^="info"] > [class^="first-part"] div div.semi-switch'
        # 定位是否有第三方平台
        if await page.locator(third_part_element).count():
            # 检测是否是已选中状态
            if 'semi-switch-checked' not in await page.eval_on_selector(third_part_element, 'div => div.className'):
                await page.locator(third_part_element).locator('input.semi-switch-native-control').click()

        if self.publish_date != 0:
            await self.set_schedule_time_douyin(page, self.publish_date)

        # 判断视频是否发布成功
        publish_start = asyncio.get_event_loop().time()
        publish_success = False
        publish_clicked = False
        max_wait = 120  # 最多等120秒
        
        while not publish_success:
            try:
                # 检查页面是否关闭
                if page.is_closed():
                    douyin_logger.success("  [-]页面已关闭，发布成功!")
                    publish_success = True
                    break
                
                # 查找发布按钮
                publish_button = page.get_by_role('button', name="发布", exact=True)
                if await publish_button.count():
                    # 检查按钮是否可用
                    is_disabled = await publish_button.get_attribute("disabled")
                    if is_disabled is None:  # 按钮可用
                        if not publish_clicked:
                            await publish_button.click()
                            publish_clicked = True
                            douyin_logger.info("  [-]已点击发布按钮，等待处理...")
                            await asyncio.sleep(1)  # 优化：减少等待时间
                
                # 尝试检测成功标志
                success_selectors = [
                    'text=发布成功',
                    'text=success',
                    '[class*="success"]',
                    'text=已发布'
                ]
                
                for selector in success_selectors:
                    if await page.locator(selector).count() > 0:
                        douyin_logger.success("  [-]检测到发布成功标志!")
                        publish_success = True
                        break
                
                if publish_success:
                    break
                
                # 检查是否跳转
                current_url = page.url
                if "manage" in current_url or "content/manage" in current_url:
                    douyin_logger.success("  [-]已跳转到管理页面，发布成功!")
                    publish_success = True
                    break
                
                # 检查是否超时
                if asyncio.get_event_loop().time() - publish_start > max_wait:
                    if publish_clicked:
                        douyin_logger.warning("  [-]发布处理中（已点击发布按钮）")
                        # 再次检查
                        await asyncio.sleep(5)
                        if page.is_closed():
                            douyin_logger.success("  [-]页面已关闭，发布成功!")
                            publish_success = True
                            break
                    break
                
                await asyncio.sleep(1)
                
            except Exception as e:
                if 'TargetClosedError' in str(e) or page.is_closed():
                    douyin_logger.success("  [-]页面已关闭，发布成功!")
                    publish_success = True
                    break
                await asyncio.sleep(1)

        # 保存cookie (页面关闭也能保存)
        try:
            if not context.is_closed():
                await context.storage_state(path=self.account_file)
                douyin_logger.success("  [-]cookie更新完毕！")
        except:
            pass  # 这里延迟是为了方便眼睛直观的观看
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()
    
    async def set_thumbnail(self, page: Page, thumbnail_path: str):
        import os
        from pathlib import Path
        
        if not thumbnail_path:
            # 自动截取视频帧作为封面
            thumbnail_path = f"/tmp/thumbnail_{os.getpid()}.jpg"
            douyin_logger.info('  [-] 未提供封面，自动截取视频帧...')
            
            # 等待视频加载并播放
            await page.wait_for_timeout(1500)
            
            # 查找视频播放器
            video_element = page.locator("video").first
            if await video_element.count() > 0:
                # 尝试点击播放让视频开始
                try:
                    await video_element.click()
                    await page.wait_for_timeout(1000)
                except:
                    pass
                
                # 截图视频帧
                await video_element.screenshot(path=thumbnail_path)
                douyin_logger.info(f'  [-] 已截取视频帧: {thumbnail_path}')
            else:
                # 如果找不到video元素，截图整个页面作为封面
                await page.screenshot(path=thumbnail_path, full_page=False)
                douyin_logger.warning('  [-] 未找到视频元素，使用页面截图作为封面')
        
        # 设置封面
        if thumbnail_path and Path(thumbnail_path).exists():
            douyin_logger.info('  [-] 正在设置视频封面...')
            
            # 点击"选择封面"
            await page.click('text="选择封面"')
            await page.wait_for_selector("div.dy-creator-content-modal", timeout=10000)
            await asyncio.sleep(1)
            
            # ========== 设置竖版封面 ==========
            douyin_logger.info('  [-] 设置竖版封面...')
            # 查找弹窗内的"设置竖封面"按钮
            shu_bian_btn = page.locator("#dialog-1 button:has-text('设置竖封面')")
            
            if await shu_bian_btn.count() == 0:
                shu_bian_btn = page.locator("div.dy-creator-content-modal button:has-text('设置竖封面')").first
            
            if await shu_bian_btn.count() > 0:
                await shu_bian_btn.click()
                await asyncio.sleep(1)
            
            # 上传竖版封面
            await page.locator("div[class^='semi-upload upload'] >> input.semi-upload-hidden-input").set_input_files(thumbnail_path)
            await asyncio.sleep(1)  # 优化：减少等待时间
            
            # 点击完成按钮（竖版设置）
            完成_btn = page.locator("div#tooltip-container button:visible:has-text('完成')")
            if await 完成_btn.count() > 0:
                await 完成_btn.click()
                douyin_logger.info('  [-] 竖版封面设置完成')
                await asyncio.sleep(1)
            
            # ========== 设置横版封面 ==========
            douyin_logger.info('  [-] 设置横版封面...')
            
            # 查找弹窗内的"设置横封面"按钮（不是tooltip里的）
            # 弹窗中的按钮在 #dialog-1 或类似容器中
            横封面_btn = page.locator("#dialog-1 button:has-text('设置横封面')")
            
            if await 横封面_btn.count() == 0:
                # 备选：在弹窗容器中查找
                横封面_btn = page.locator("div.dy-creator-content-modal button:has-text('设置横封面')").first
            
            if await 横封面_btn.count() > 0:
                await 横封面_btn.click()
                douyin_logger.info('  [-] 已点击横版封面设置按钮')
                await asyncio.sleep(1)
            else:
                douyin_logger.warning('  [-] 未找到横版封面设置按钮，尝试使用tooltip中的')
                横封面_btn = page.locator("#tooltip-container button:has-text('设置横封面')").first
                await 横封面_btn.click()
            
            await asyncio.sleep(1)
            
            # 上传横版封面
            await page.locator("div[class^='semi-upload upload'] >> input.semi-upload-hidden-input").set_input_files(thumbnail_path)
            await asyncio.sleep(1)  # 优化：减少等待时间
            
            # 点击完成按钮（横版设置）
            完成_btn = page.locator("div#tooltip-container button:visible:has-text('完成')")
            if await 完成_btn.count() > 0:
                await 完成_btn.click()
                douyin_logger.info('  [-] 横版封面设置完成')
                await asyncio.sleep(1)
            
            # ========== 点击主完成按钮关闭弹窗 ==========
            douyin_logger.info('  [-] 等待封面设置弹窗关闭...')
            
            # 查找所有"完成"按钮并点击最后一个（通常是主完成按钮）
            完成按钮们 = page.locator("div.dy-creator-content-modal button:has-text('完成')")
            count = await 完成按钮们.count()
            
            if count > 0:
                # 点击最后一个完成按钮
                await 完成按钮们.nth(count - 1).click()
                douyin_logger.info(f'  [-] 已点击完成按钮 ({count}个按钮中第{count}个)')
                await asyncio.sleep(2)
            
            # 强制等待并检查
            await asyncio.sleep(2)
            
            # 尝试多种方式关闭
            closed = False
            for attempt in range(3):
                # 检查是否还在弹窗中
                modal = page.locator("div.dy-creator-content-modal")
                if await modal.count() == 0:
                    closed = True
                    break
                
                douyin_logger.info(f'  [-] 关闭弹窗尝试 {attempt + 1}/3...')
                
                # 方式1: 按ESC
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
                
                # 方式2: 点击确定/完成按钮
                ok_btn = page.locator("button:has-text('确定'), button:has-text('完成'), button:has-text('确认')")
                if await ok_btn.count() > 0:
                    await ok_btn.last.click()
                    await asyncio.sleep(1)
                
                # 方式3: 点击遮罩层外部
                await page.click("body", position={"x": 5, "y": 5})
                await asyncio.sleep(1)
            
            if await page.locator("div.dy-creator-content-modal").count() == 0:
                douyin_logger.info('  [+] 封面设置弹窗已关闭')
            else:
                douyin_logger.warning('  [+] 封面设置弹窗可能仍存在，继续尝试发布...')
            
            douyin_logger.info('  [+] 视频封面设置完成！')
            
            # 删除临时封面文件
            try:
                Path(thumbnail_path).unlink()
            except:
                pass
            
            douyin_logger.info('  [-] 封面设置完成，准备发布...')
            await asyncio.sleep(1)
            

    async def set_location(self, page: Page, location: str = ""):
        if not location:
            return
        # todo supoort location later
        # await page.get_by_text('添加标签').locator("..").locator("..").locator("xpath=following-sibling::div").locator(
        #     "div.semi-select-single").nth(0).click()
        await page.locator('div.semi-select span:has-text("输入地理位置")').click()
        await page.keyboard.press("Backspace")
        await page.wait_for_timeout(1000)
        await page.keyboard.type(location)
        await page.wait_for_selector('div[role="listbox"] [role="option"]', timeout=5000)
        await page.locator('div[role="listbox"] [role="option"]').first.click()

    async def set_ai_generated(self, page: Page):
        """设置 AI 生成内容标记 - 抖音创作者中心"""
        if not self.ai_generated:
            return True
        
        douyin_logger.info("  [-] 正在设置 AI 生成内容标记...")
        
        # 先关闭可能存在的弹窗
        await self.close_popups(page)
        
        # 步骤1: 找到并点击"发文助手"
        douyin_logger.info("  [-] 步骤1: 查找发文助手...")
        fasong_selectors = [
            'div:has-text("发文助手"):not(:has(div))',
            'span:has-text("发文助手")',
            'text=发文助手',
            '[class*="assistant"]:has-text("发文")',
        ]
        
        fasong_clicked = False
        for selector in fasong_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                for i in range(count):
                    element = elements.nth(i)
                    if await element.is_visible():
                        await element.click()
                        douyin_logger.info(f"  [-] 已点击发文助手")
                        fasong_clicked = True
                        await asyncio.sleep(1)
                        break
                if fasong_clicked:
                    break
            except:
                continue
        
        if not fasong_clicked:
            douyin_logger.warning("  [-] 未找到发文助手，尝试其他方式...")
        
        # 步骤2: 找到并点击"自主声明"或"修改声明"
        await asyncio.sleep(1)
        douyin_logger.info("  [-] 步骤2: 查找自主声明...")
        declare_selectors = [
            'text=自主声明',
            'text=修改声明',
            'span:has-text("自主声明")',
            'span:has-text("修改声明")',
            'div:has-text("声明")',
        ]
        
        declare_clicked = False
        for selector in declare_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0 and await element.is_visible():
                    await element.click()
                    douyin_logger.info(f"  [-] 已点击声明选项")
                    declare_clicked = True
                    await asyncio.sleep(1)
                    break
            except:
                continue
        
        # 步骤3: 勾选"内容由AI生成"或类似选项
        await asyncio.sleep(1)
        douyin_logger.info("  [-] 步骤3: 勾选AI生成选项...")
        ai_checkbox_selectors = [
            # 包含"AI"文本的复选框
            'label:has-text("AI") input[type="checkbox"]',
            'div:has-text("AI生成") input',
            'div:has-text("内容由AI生成") input',
            'span:has-text("AI生成")',
            'span:has-text("内容由AI生成")',
            # 通过父级定位
            'div:has-text("作者声明") input[type="checkbox"]',
            'div:has-text("内容由") input[type="checkbox"]',
            # 备选：包含"生成"的选项
            'label:has-text("生成") input[type="checkbox"]',
            # 新版选项
            '[class*="ai"] input[type="checkbox"]',
            '[class*="AI"] input[type="checkbox"]',
        ]
        
        for selector in ai_checkbox_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                for i in range(count):
                    element = elements.nth(i)
                    if await element.is_visible():
                        # 检查是否已勾选
                        is_checked = await element.evaluate('el => el.checked || el.getAttribute("aria-checked") === "true"')
                        if not is_checked:
                            await element.click()
                            douyin_logger.info(f"  [-] 已勾选 AI 生成内容: {selector}")
                            await asyncio.sleep(0.5)
                            return True
                        else:
                            douyin_logger.info("  [-] AI 生成内容已勾选")
                            return True
            except:
                continue
        
        # 尝试通过文本搜索所有复选框
        try:
            checkboxes = page.locator('input[type="checkbox"], div[role="checkbox"]')
            count = await checkboxes.count()
            for i in range(count):
                try:
                    checkbox = checkboxes.nth(i)
                    parent = checkbox.locator('xpath=ancestor::div[1]')
                    parent_text = await parent.inner_text()
                    if 'AI' in parent_text or '生成' in parent_text or '声明' in parent_text:
                        is_checked = await checkbox.evaluate('el => el.checked || el.getAttribute("aria-checked") === "true"')
                        if not is_checked:
                            await checkbox.click()
                            douyin_logger.info("  [-] 已勾选 AI 生成内容 (通过文本搜索)")
                            return True
                except:
                    continue
        except:
            pass
        
        douyin_logger.warning("  [-] 未找到 AI 生成内容选项，可能该账号无需此选项或页面结构已变化")
        return False

    async def close_popups(self, page: Page):
        """关闭可能存在的弹窗"""
        close_selectors = [
            # 关闭按钮
            'button[aria-label="关闭"]',
            'button[aria-label="Close"]',
            'button:has-text("关闭")',
            'button:has-text("Close")',
            'button:has-text("取消")',
            'button:has-text("Cancel")',
            'button:has-text("知道了")',
            'button:has-text("确定")',
            'button:has-text("确定")',
            # 关闭图标
            'div[class*="close"]',
            'span[class*="close"]',
            '[class*="modal-close"]',
            '[class*="dialog-close"]',
            # 遮罩层
            'div[class*="mask"]',
            'div[class*="overlay"]',
        ]
        
        for selector in close_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0 and await element.is_visible():
                    await element.click(timeout=1000)
                    douyin_logger.info(f"  [-] 已关闭弹窗: {selector}")
                    await asyncio.sleep(0.5)
            except:
                pass
        
        # 按 ESC 键关闭弹窗
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.3)

    async def handle_product_dialog(self, page: Page, product_title: str):
        """处理商品编辑弹窗"""

        await page.wait_for_timeout(1000)
        await page.wait_for_selector('input[placeholder="请输入商品短标题"]', timeout=10000)
        short_title_input = page.locator('input[placeholder="请输入商品短标题"]')
        if not await short_title_input.count():
            douyin_logger.error("[-] 未找到商品短标题输入框")
            return False
        product_title = product_title[:10]
        await short_title_input.fill(product_title)
        # 等待一下让界面响应
        await page.wait_for_timeout(1000)

        finish_button = page.locator('button:has-text("完成编辑")')
        if 'disabled' not in await finish_button.get_attribute('class'):
            await finish_button.click()
            douyin_logger.debug("[+] 成功点击'完成编辑'按钮")
            
            # 等待对话框关闭
            await page.wait_for_selector('.semi-modal-content', state='hidden', timeout=5000)
            return True
        else:
            douyin_logger.error("[-] '完成编辑'按钮处于禁用状态，尝试直接关闭对话框")
            # 如果按钮禁用，尝试点击取消或关闭按钮
            cancel_button = page.locator('button:has-text("取消")')
            if await cancel_button.count():
                await cancel_button.click()
            else:
                # 点击右上角的关闭按钮
                close_button = page.locator('.semi-modal-close')
                await close_button.click()
            
            await page.wait_for_selector('.semi-modal-content', state='hidden', timeout=5000)
            return False
        
    async def set_product_link(self, page: Page, product_link: str, product_title: str):
        """设置商品链接功能"""
        await page.wait_for_timeout(1000)  # 优化：减少等待时间
        try:
            # 定位"添加标签"文本，然后向上导航到容器，再找到下拉框
            await page.wait_for_selector('text=添加标签', timeout=10000)
            dropdown = page.get_by_text('添加标签').locator("..").locator("..").locator("..").locator(".semi-select").first
            if not await dropdown.count():
                douyin_logger.error("[-] 未找到标签下拉框")
                return False
            douyin_logger.debug("[-] 找到标签下拉框，准备选择'购物车'")
            await dropdown.click()
            ## 等待下拉选项出现
            await page.wait_for_selector('[role="listbox"]', timeout=5000)
            ## 选择"购物车"选项
            await page.locator('[role="option"]:has-text("购物车")').click()
            douyin_logger.debug("[+] 成功选择'购物车'")
            
            # 输入商品链接
            ## 等待商品链接输入框出现
            await page.wait_for_selector('input[placeholder="粘贴商品链接"]', timeout=5000)
            # 输入
            input_field = page.locator('input[placeholder="粘贴商品链接"]')
            await input_field.fill(product_link)
            douyin_logger.debug(f"[+] 已输入商品链接: {product_link}")
            
            # 点击"添加链接"按钮
            add_button = page.locator('span:has-text("添加链接")')
            ## 检查按钮是否可用（没有disable类）
            button_class = await add_button.get_attribute('class')
            if 'disable' in button_class:
                douyin_logger.error("[-] '添加链接'按钮不可用")
                return False
            await add_button.click()
            douyin_logger.debug("[+] 成功点击'添加链接'按钮")
            ## 如果链接不可用
            await page.wait_for_timeout(1000)
            error_modal = page.locator('text=未搜索到对应商品')
            if await error_modal.count():
                confirm_button = page.locator('button:has-text("确定")')
                await confirm_button.click()
                # await page.wait_for_selector('.semi-modal-content', state='hidden', timeout=5000)
                douyin_logger.error("[-] 商品链接无效")
                return False

            # 填写商品短标题
            if not await self.handle_product_dialog(page, product_title):
                return False
            
            # 等待链接添加完成
            douyin_logger.debug("[+] 成功设置商品链接")
            return True
        except Exception as e:
            douyin_logger.error(f"[-] 设置商品链接时出错: {str(e)}")
            return False

    async def locate_first_visible(self, page: Page, selectors, timeout=5000):
        """
        Try selectors sequentially and return the first visible locator.
        """
        for selector in selectors:
            locator = page.locator(selector).first
            if not await locator.count():
                continue
            try:
                await locator.wait_for(state="visible", timeout=timeout)
                return locator
            except PlaywrightTimeoutError:
                continue
        return None

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

