# !/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
基本配置文件
"""
from src.config.common_config import CommonConstant


class LickConfig:
    # "kch","yd", "wh"
    lickType = "yd"

    extConfig = {
        CommonConstant.kchType: {
            "login": "",
            "password_hash": "",
            "rating": ["safe", "questionable", "explicit"],
            "ext_param": {"rating": ["safe", "questionable", "explicit"]},
        },
        CommonConstant.ydType: {
            "login": "",
            "password_hash": "",
            "ext_param": {"rating": ["safe", "questionable", "explicit"]},
        },
        CommonConstant.whType: {
            "username": "",
            "password": "",
            "api_key": "",
            "ext_param": {
                "category": ["anime", "general", "people"],
                "category_map": {"anime": "100", "general": "010", "people": "001"},
                "rating": ["sfw", "sketchy", "nsfw"],
                "rating_map": {"sfw": "100", "sketchy": "010", "nsfw": "001"},
            },
        },
    }
