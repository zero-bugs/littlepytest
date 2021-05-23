# !/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
基本配置文件
"""


class CommonConstant:
    whType = "wh"
    kchType = "kch"
    ydType = "yd"

    basicConfig = {
        kchType: {
            "sourceAddress": [""],
            "dbLibPath": "./dao/konachan.dao",
            "picOutputPath": "",
            "exportHisList": "kch.filelist.history",
        },
        ydType: {
            "sourceAddress": [""],
            "dbLibPath": "./dao/yande.dao",
            "picOutputPath": "",
            "exportHisList": "yd.filelist.history",
        },
        whType: {
            "sourceAddress": [""],
            "dbLibPath": "./dao/wallpaper.dao",
            "picOutputPath": "",
            "exportHisList": "wh.filelist.history",
        },
    }

    """公共配置文件"""
    time_format = "%Y-%m-%d %H:%M:%S"
