#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import time
import requests

from common.common_config import konachanUrl
from common.proxy_config import proxies


class KcScrawlImpl:
    def scrawlPicUseApi(self, page=1, limit=100):
        url = '%s/post.json?page=%d&limit=%d' % (konachanUrl, page, limit)
        resp = self.httpRetryExecutor(url, limit, page)
        if resp is None or resp.status_code != 200:
            print('url:%s,status code:%d' % (url, resp.status_code))
            return

        print("$s" % resp.content)
        for p in json.loads(resp.content):
            print(p)

    def httpRetryExecutor(self, url, limit, page):
        for num in range(0, 5):
            try:
                resp = requests.get(url, proxies=proxies, verify=True, timeout=600)
                return resp
            except Exception as err:
                print("http request failed, url:" + url)
                print(err)
                time.sleep(5)
                continue
