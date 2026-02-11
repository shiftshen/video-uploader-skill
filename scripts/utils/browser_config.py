# -*- coding: utf-8 -*-
"""
Enhanced browser configuration for bypassing platform detection
"""
from pathlib import Path
from typing import Dict, List, Optional


def get_chromium_args() -> List[str]:
    """
    Get Chromium launch arguments to bypass detection
    """
    return [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-infobars',

        '--ignore-certifcate-errors',
        '--ignore-certifcate-errors-spki-list',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-extensions',
        '--disable-default-apps',
        '--disable-sync',
        '--disable-translate',
        '--hide-scrollbars',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-first-run',
        '--safebrowsing-disable-auto-update',
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-client-side-phishing-detection',
        '--disable-component-extensions-with-background-pages',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-popup-blocking',
        '--disable-prompt-on-repost',
        '--disable-renderer-backgrounding',
        '--force-color-profile=srgb',
        '--disable-features=TranslateUI,BlinkGenPropertyTrees',
    ]


def get_firefox_args() -> List[str]:
    """
    Get Firefox launch arguments
    """
    return [
        '--lang=en-GB',
    ]


def get_chromium_context_options() -> Dict:
    """
    Get Chromium browser context options
    """
    return {
        'viewport': {'width': 1920, 'height': 1080},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'locale': 'zh-CN',
        'timezone_id': 'Asia/Shanghai',
        'permissions': ['geolocation', 'notifications'],
        'geolocation': {'latitude': 39.9042, 'longitude': 116.4074},  # Beijing
        'color_scheme': 'light',
        'accept_downloads': True,
        'ignore_https_errors': True,
    }


def get_firefox_context_options() -> Dict:
    """
    Get Firefox browser context options
    """
    return {
        'viewport': {'width': 1920, 'height': 1080},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'locale': 'en-US',
        'timezone_id': 'America/New_York',
        'permissions': ['geolocation', 'notifications'],
        'color_scheme': 'light',
        'accept_downloads': True,
        'ignore_https_errors': True,
    }


async def setup_browser_context(context, stealth_js_path: Optional[Path] = None):
    """
    Setup browser context with anti-detection scripts
    
    Args:
        context: Playwright browser context
        stealth_js_path: Path to stealth.min.js file
    
    Returns:
        Configured browser context
    """
    # Add stealth script if provided
    if stealth_js_path and stealth_js_path.exists():
        await context.add_init_script(path=stealth_js_path)
    
    # Add additional anti-detection scripts
    await context.add_init_script("""
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        
        // Override chrome property
        window.chrome = {
            runtime: {}
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    return context


def get_platform_specific_config(platform: str) -> Dict:
    """
    Get platform-specific browser configuration
    
    Args:
        platform: Platform name (douyin, kuaishou, tiktok, tencent, xhs)
    
    Returns:
        Platform-specific configuration dictionary
    """
    configs = {
        'douyin': {
            'browser': 'chromium',
            'headless': False,
            'args': get_chromium_args(),
            'context_options': get_chromium_context_options(),
        },
        'kuaishou': {
            'browser': 'chromium',
            'headless': False,
            'args': get_chromium_args(),
            'context_options': get_chromium_context_options(),
        },
        'tiktok': {
            'browser': 'firefox',
            'headless': False,
            'args': get_firefox_args(),
            'context_options': get_firefox_context_options(),
        },
        'tencent': {
            'browser': 'chromium',
            'headless': False,
            'args': get_chromium_args(),
            'context_options': get_chromium_context_options(),
        },
        'xhs': {
            'browser': 'chromium',
            'headless': False,
            'args': get_chromium_args(),
            'context_options': get_chromium_context_options(),
        },
    }
    
    return configs.get(platform, configs['douyin'])
