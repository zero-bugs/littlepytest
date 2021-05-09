#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import datetime
import json
import os
import threading
import time
import requests

from common.common_config import CommonConstant

from common.proxy_config import ProxyConstant
from db.sq_connection import sqliteManager
from models.pic_attr import PicAttr

historyImgList = []


class KcScrawlImpl:
    def init(self):
        with open(CommonConstant.downloadImgList) as f:
            for line in f.readlines():
                historyImgList.append(line.strip())
        print(f"init completed, history file count:{len(historyImgList)}")

    def scrawlPicUseApi(self, page=1, limit=100, start_time=None):
        url = "%s/post.json?page=%d&limit=%d" % (
            CommonConstant.konachanUrl,
            page,
            limit,
        )
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.198 Safari/537.36",
            "referer": "https://konachan.com/post",
        }

        resp = self.httpRetryExecutor(url, headers)
        if resp is None:
            print("response is none, url:%s" % url)
            return False
        elif resp.status_code != 200:
            print("url:%s,status code:%d" % (url, resp.status_code))
            return False

        start_time = datetime.datetime.strptime(start_time, CommonConstant.time_format)
        start_time = start_time.timestamp()

        pics = list()
        item_nums = 0
        item_nums_no = 0
        for p in json.loads(resp.content):
            item_nums_no += 1
            pic = PicAttr()
            pic.id = p.get("id")
            pic.width = p.get("width")
            pic.height = p.get("height")
            pic.file_size = p.get("file_size")
            pic.score = p.get("score")
            pic.md5 = p.get("md5")
            pic.previewUrl = p.get("preview_url")
            pic.fileUrl = p.get("file_url")
            pic.tags = p.get("tags")
            pic.create_at = p.get("created_at")
            pic.creator_id = p.get("creator_id")
            pic.author = p.get("author")
            pic.source = p.get("source")

            if pic.create_at - start_time > 0:
                if self.downloadOnePic(pic):
                    pics.append(pic)
            else:
                item_nums += 1
        else:
            return sqliteManager.batchInsertImg(pics)

    def httpRetryExecutor(self, url, headers: dict):
        retry = False
        for num in range(0, 5):
            if retry:
                print("retry url:%s" % url)
            try:
                if ProxyConstant.proxySwitch:
                    return requests.get(
                        url,
                        proxies=ProxyConstant.proxies,
                        verify=True,
                        timeout=300,
                        headers=headers,
                    )
                else:
                    return requests.get(url, verify=True, timeout=300)
            except Exception as err:
                print("http request failed, retry url:" + url)
                print(err)

                time.sleep(5)

                retry = True
                if num == 4:
                    print("failed at last, please try by hands.")
                    return None

    def scrawPicUseApiAllLatest(self, start_page=1, end_page=1000, start_time=None):
        currentPage = start_page
        while currentPage < end_page:
            print(
                "begin to scrawl, current page:%d"
                % currentPage
            )
            val = self.scrawlPicUseApi(currentPage, 20, start_time)
            print(
                "end with scrawl, current page:%d, total page"
                % currentPage
            )
            print("..")
            time.sleep(1)
            if val:
                currentPage += 1
            else:
                print(
                    "done with all scrawl, current page:%d"
                    % currentPage
                )
                break

    def downloadOnePic(self, pic: PicAttr, downloadPath=CommonConstant.picOutputPath):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.198 Safari/537.36",
            "referer": "https://konachan.com/post",
        }
        # check dir
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)

        suffix = ".jpg"
        pos = pic.fileUrl.rfind(".")
        if pos != -1:
            suffix = pic.fileUrl[pos:]
        filename = f"{downloadPath}/{pic.id}{suffix}"
        if f"{pic.id}{suffix}" in historyImgList or os.path.exists(filename):
            print("file id:{0} has exist".format(pic.id))
            return True

        print(
            "{}-begin to download,id:{},name:{},time:{},url:{}".format(
                threading.current_thread().name,
                pic.id,
                filename,
                time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()),
                pic.fileUrl,
            )
        )
        response = self.httpRetryExecutor(pic.fileUrl, headers)
        print(
            "{0}-begin to write,id:{1}, time:{2},path:{3}".format(
                threading.current_thread().name,
                pic.id,
                time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()),
                filename,
            )
        )
        if response is None:
            return False

        with open(filename, "wb") as f:
            f.write(response.content)
        print(
            "{}-end to write,id:{},time:{},path:{}".format(
                threading.current_thread().name,
                pic.id,
                time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()),
                filename,
            )
        )

        return True

    def downloadPicFromDb(
            self, start=0, maxCount=100000, downloadPath=CommonConstant.picOutputPath
    ):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.198 Safari/537.36",
            "referer": "https://konachan.com/post",
        }

        # check dir
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)

        limit = 500
        offset = start
        while True:
            if offset >= maxCount:
                print("done all task {0}".format(offset))
                break

            val = sqliteManager.selectImgs(limit=limit, offset=offset)
            offset += limit
            if val is None or len(val) == 0:
                break
            else:
                print(
                    "{}-current offset: {}".format(
                        threading.current_thread().name, offset
                    )
                )
                for pic in val:
                    suffix = ".jpg"
                    pos = pic[7].rfind(".")
                    if pos != -1:
                        suffix = pic[7][pos:]
                    filename = f"{downloadPath}/{pic[0]}{suffix}"
                    if f"{pic[0]}{suffix}" in historyImgList or os.path.exists(
                            filename
                    ):
                        # print("file id:{0} has exist".format(pic[0]))
                        continue
                    else:
                        print(
                            "{}-begin to download,id:{},name:{},time:{},url:{}".format(
                                threading.current_thread().name,
                                pic[0],
                                filename,
                                time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()),
                                pic[7],
                            )
                        )
                        response = self.httpRetryExecutor(pic[7], headers)
                        print(
                            "{0}-begin to write,id:{1}, time:{2},path:{3}".format(
                                threading.current_thread().name,
                                pic[0],
                                time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()),
                                filename,
                            )
                        )
                        if response is None:
                            continue

                        with open(filename, "wb") as f:
                            f.write(response.content)
                        print(
                            "{}-end to write,id:{},time:{},path:{}".format(
                                threading.current_thread().name,
                                pic[0],
                                time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()),
                                filename,
                            )
                        )
