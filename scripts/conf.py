# -*- coding: utf-8 -*-
"""
Configuration file for video uploader skill
"""
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Chrome path (optional, leave empty to use system default)
LOCAL_CHROME_PATH = ""

# XHS Server (for xiaohongshu signature) - 需要签名服务
XHS_SERVER = "http://localhost:5005"
