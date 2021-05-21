# !/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
基本配置文件
"""


class CommonConstant:
    basicConfig = {
        "kch": {
            "sourceAddress": ["https://konachan.com"],
            "dbLibPath": "./dao/konachan.dao",
            "picOutputPath": "D://konachan",
            "exportHisList": 'kch.filelist.history'
        },
        "yd": {
            "sourceAddress": ["https://oreno.imouto.us", "https://yande.in"],
            "dbLibPath": "./dao/yande.dao",
            "picOutputPath": "D://yande",
            "exportHisList": 'yd.filelist.history'
        },
        "wp": {
            "sourceAddress": ["https://wallhaven.cc"],
            "dbLibPath": "./dao/wallpaper.dao",
            "picOutputPath": "D://wallpaper",
            "exportHisList": 'wp.filelist.history'
        }
    }

    """公共配置文件"""
    time_format = "%Y-%m-%d %H:%M:%S"
