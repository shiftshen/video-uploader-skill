# -*- coding: utf-8 -*-
"""
Configuration file for video uploader skill
"""
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Chrome path (optional, leave empty to use system default)
LOCAL_CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# XHS Server (for xiaohongshu signature)
XHS_SERVER = "http://localhost:5005"
