# !/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
基本配置文件
"""


class LickConfig:
    lickType = 'yd'

    extConfig = {
        "kch": {
        },
        "yd": {
            "login": "",
            "password_hash": ""
        },
        "wp": {
            "username": "",
            "password": "",
            "api_key": "",
            "category_type_db": ['anime', 'general', 'people'],
            "category_map": {'anime': '100', 'general': '010', 'people': '001'},
            "purity_type_db": ['sfw', 'sketchy', 'nsfw'],
            "purity_map": {'sfw': '100', 'sketchy': '010', 'nsfw': '001'},
        }
    }
