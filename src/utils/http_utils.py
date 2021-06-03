import time

import requests

from src.config.common_config import CommonConstant
from src.config.lick_config import LickConfig
from src.config.proxy_config import ProxyConstant
from src.logs.log_utils import LogUtils


def getUrlAddress():
    return CommonConstant.basicConfig[LickConfig.lickType].get("sourceAddress")[0]


def getUrlHost():
    return CommonConstant.basicConfig[LickConfig.lickType].get("sourceAddress")[0].split("//")[-1]


commonHeaders = {
    "Host": getUrlHost(),
    "Referer": getUrlAddress(),
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW 64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE ",
}


def httpRetryExecutorWithRetry(url, extParams: dict, extHeaders: dict, payload: dict, method="GET"):
    retry = False
    for num in range(0, 5):
        if retry:
            LogUtils.log(f"retry url:{url}")
        try:
            result = httpRequest(url, extParams, extHeaders, method=method, payload=payload)
            if result[0] is False:
                retry = True
                time.sleep(5)
            else:
                return result[1]
        except Exception as err:
            LogUtils.log(f"http request failed, retry url:{url}")
            LogUtils.log(err)

            time.sleep(5)

            retry = True
            if num == 4:
                LogUtils.log("failed at last, please try by hands.")
                return None


def httpRequest(url, extParams: dict, extHeaders: dict, payload: dict, method="GET"):
    if method == "GET":
        return exeGetRequest(url, extParams, extHeaders)
    elif method == "POST":
        return exePostRequest(url, extHeaders, payload)


def exeGetRequest(url, extParams, extHeaders):
    """执行get请求"""
    if ProxyConstant.proxySwitch:
        resp = requests.get(
            url,
            proxies=ProxyConstant.proxies,
            verify=True,
            timeout=300,
            params=extParams,
            headers=extHeaders,
        )
    else:
        resp = requests.get(
            url,
            verify=True,
            timeout=300,
            params=extParams,
            headers=extHeaders)

    if resp is None:
        return [
            False,
        ]
    elif resp.status_code >= 400:
        LogUtils.log(f"url:{url},status code:{resp.status_code}, need retry.")
        return [False, resp]
    else:
        return [True, resp]


def exePostRequest(url, extHeaders, payload):
    """执行POST请求"""
    if ProxyConstant.proxySwitch:
        resp = requests.post(
            url, proxies=ProxyConstant.proxies,
            verify=True,
            timeout=300,
            headers=extHeaders,
            payload=payload
        )
    else:
        resp = requests.post(
            url,
            verify=True,
            timeout=300,
            headers=extHeaders,
            payload=payload)

    if resp is None:
        return [False]
    elif resp.status_code >= 400:
        LogUtils.log(f"url:{url},status code:{resp.status_code}, need retry.")
        return [False, resp]
    else:
        return [True, resp]
