# !/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
代理配置
"""


class ProxyConstant:
    proxies = {
        "http": "http://username:password@host:port",
        "https": "http://username:password@host:port",
    }
    proxySwitch = False
