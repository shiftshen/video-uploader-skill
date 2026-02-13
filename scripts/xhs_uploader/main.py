import configparser
import json
import pathlib
from time import sleep
import asyncio
from concurrent.futures import ThreadPoolExecutor

import requests
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

from conf import BASE_DIR, XHS_SERVER, LOCAL_CHROME_PATH

config = configparser.RawConfigParser()
config.read('accounts.ini')


def _get_signature_sync(uri, data, a1, web_session):
    """Synchronous wrapper to get signature"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_get_signature_async(uri, data, a1, web_session))
    finally:
        loop.close()


async def _get_signature_async(uri, data=None, a1="", web_session=""):
    """Async signature function"""
    for _ in range(10):
        try:
            async with async_playwright() as playwright:
                stealth_js_path = pathlib.Path(BASE_DIR / "utils/stealth.min.js")
                chromium = playwright.chromium

                if LOCAL_CHROME_PATH:
                    browser = await chromium.launch(headless=True, executable_path=LOCAL_CHROME_PATH)
                else:
                    browser = await chromium.launch(headless=True)

                browser_context = await browser.new_context()
                await browser_context.add_init_script(path=stealth_js_path)
                context_page = await browser_context.new_page()
                await context_page.goto("https://www.xiaohongshu.com")
                
                cookies = []
                if a1:
                    cookies.append({'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"})
                if web_session:
                    cookies.append({'name': 'web_session', 'value': web_session, 'domain': ".xiaohongshu.com", 'path': "/"})
                if cookies:
                    await browser_context.add_cookies(cookies)
                
                await context_page.reload()
                await asyncio.sleep(2)
                encrypt_params = await context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                await browser.close()
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception as e:
            print(f"Sign attempt failed: {e}")
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")


def sign_local(uri, data=None, a1="", web_session=""):
    """Local signature function - runs in thread to avoid blocking async loop"""
    # Run in thread pool to avoid blocking
    with ThreadPoolExecutor() as executor:
        future = executor.submit(_get_signature_sync, uri, data, a1, web_session)
        return future.result()


def sign(uri, data=None, a1="", web_session=""):
    # 填写自己的 flask 签名服务端口地址
    res = requests.post(f"{XHS_SERVER}/sign",
                        json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
    signs = res.json()
    return {
        "x-s": signs["x-s"],
        "x-t": signs["x-t"]
    }


def beauty_print(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))
