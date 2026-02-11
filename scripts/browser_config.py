# -*- coding: utf-8 -*-
"""
共享浏览器配置 - 解决自动化检测问题
"""
from pathlib import Path

# Chrome 路径配置
LOCAL_CHROME_PATH = ""

# 默认 User-Agent
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 浏览器上下文配置
BROWSER_CONTEXT_CONFIG = {
    "locale": "en-US",
    "user_agent": DEFAULT_USER_AGENT,
    "extra_http_headers": {
        "Accept-Language": "en-US,en;q=0.9"
    },
    "accept_downloads": True,
    "bypass_csp": True
}


def get_browser_launch_options(chrome_path=""):
    """获取浏览器启动参数"""
    if chrome_path:
        return {
            "headless": False,
            "executable_path": chrome_path,
            "channel": "chrome"
        }
    return {
        "headless": False,
        "channel": "chrome"
    }
