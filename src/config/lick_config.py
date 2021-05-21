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
            "login": "singleman",
            "password_hash": "04pz5oT1l2g-FQgd2TAsqA"
        },
        "wp": {
            "username": "singleman",
            "password": "xxxx",
            "api_key": "DBQVNwjRpoVJCv4PfjW1QfxeUhEDP6Qj",
            "category_type_db": ['anime', 'general', 'people'],
            "category_map": {'anime': '100', 'general': '010', 'people': '001'},
            "purity_type_db": ['sfw', 'sketchy', 'nsfw'],
            "purity_map": {'sfw': '100', 'sketchy': '010', 'nsfw': '001'},
        }
    }
