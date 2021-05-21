# !/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
日志
"""
import threading
from datetime import datetime

from src.config.common_config import CommonConstant


class LogUtils:
    @staticmethod
    def log(msg):
        print(f"{threading.current_thread().name}-{datetime.now().strftime(CommonConstant.time_format)}-{msg}")
