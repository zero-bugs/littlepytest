#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import datetime
import json
import os
import threading
import time
import requests

from src.config.common_config import CommonConstant
from src.config.lick_config import LickConfig

from src.config.proxy_config import ProxyConstant
from src.dao.sq_connection import sqliteManager, SqliteManager
from src.logs.log_utils import LogUtils
from src.models.BaseImgMeta import BaseImgMeta

historyImgList = list()


def currentTimeStdFmt():
    return time.strftime(CommonConstant.time_format, time.localtime())


class ScrawlServiceImpl:
    def init(self):
        historyFile = CommonConstant.basicConfig[LickConfig.lickType].get(
            "exportHisList"
        )
        if os.path.exists(historyFile):
            with open(historyFile) as f:
                for line in f.readlines():
                    historyImgList.append(line.strip())
        print(f"init completed, history file count: {len(historyImgList)}")

    def scrawlPicUseApi(self, page=1, limit=100):
        """
        首次抓取所有图片存到数据库中
        :param page:页码，第1页不加入url中
        :param limit:单页数量
        :return:
        """
        url = self.getPostUrl(LickConfig.lickType, limit, page)
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.198 Safari/537.36",
            "referer": CommonConstant.basicConfig[LickConfig.lickType].get(
                "sourceAddress"
            ),
        }

        LogUtils.log(f"begin to request all images totally, url:{url}")

        resp = self.httpRetryExecutor(url, headers)
        if resp is None:
            print("response is none, url:%s" % url)
            return False
        elif resp.status_code != 200:
            print("url:%s,status code:%d" % (url, resp.status_code))
            return False

        imgs = list()
        for p in json.loads(resp.content):
            img = self.constructRemoteImg(p)
            imgs.append(img)
        else:
            SqliteManager.batchInsertImg(imgs)

    def scrawlPicUseApiLatest(self, page=1, limit=100, start_time=None):
        """
        首次抓取所有图片存到数据库中
        :param page:页码
        :param limit:单页数量
        :param start_time:开始时间
        :return:
        """
        url = self.getPostUrl(LickConfig.lickType, limit, page)
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.198 Safari/537.36",
            "referer": CommonConstant.basicConfig[LickConfig.lickType]["sourceAddress"],
        }

        LogUtils.log(f"begin to request latest iamges from some time, url:{url}")

        resp = self.httpRetryExecutor(url, headers)
        if resp is None:
            print("response is none, url:%s" % url)
            return False
        elif resp.status_code != 200:
            print("url:%s,status code:%d" % (url, resp.status_code))
            return False

        if start_time is None:
            start_time = datetime.datetime.strptime(
                "1970-01-01 00:00:00", CommonConstant.time_format
            )
        else:
            start_time = datetime.datetime.strptime(
                start_time, CommonConstant.time_format
            )

        imgs = list()
        itemNumsAll = 0
        itemNumsNoNeedDld = 0
        for p in json.loads(resp.content):
            itemNumsAll += 1
            img = self.constructRemoteImg(p)
            if datetime.datetime.fromtimestamp(p.get("created_at")) > start_time:
                if self.downloadOnePic(img):
                    imgs.append(img)
                else:
                    LogUtils.log(f"pic:{img.file_url} download failed.")
            else:
                itemNumsNoNeedDld += 1
        else:
            if not SqliteManager.batchInsertImg(imgs):
                LogUtils.log("batch insert images failed.")
                return False

        if itemNumsAll == itemNumsNoNeedDld:
            LogUtils.log("all task done...")
            return True
        return False

    def constructRemoteImg(self, imgDbObj, lickType=LickConfig.lickType):
        img = BaseImgMeta()
        img.img_id = imgDbObj.get("id")
        img.file_size = imgDbObj.get("file_size")

        if lickType == "kch" or lickType == "yd":
            img.width = imgDbObj.get("width")
            img.height = imgDbObj.get("height")
            img.file_url = imgDbObj.get("file_url")
            img.file_ext = imgDbObj.get("file_url").split(".")[-1]
            img.tags = imgDbObj.get("tags")
            img.md5 = imgDbObj.get("md5")
            img.score = imgDbObj.get("score")
            img.author = imgDbObj.get("author")
            img.creator_id = imgDbObj.get("creator_id")
            img.img_source = imgDbObj.get("source")
            img.create_at = datetime.datetime.fromtimestamp(
                imgDbObj.get("created_at")
            ).strftime(CommonConstant.time_format)
        elif lickType == "wp":
            img.width = imgDbObj.get("dimension_x")
            img.height = imgDbObj.get("dimension_y")
            img.file_url = imgDbObj.get("path")
            img.file_ext = imgDbObj.get("path").split(".")[-1]
            img.score = imgDbObj.get("favorites")
            img.create_at = datetime.datetime.strptime(
                imgDbObj.get("created_at"), CommonConstant.time_format
            )
        else:
            LogUtils.log(f"don't support this type:{lickType} for now..")

        return img

    def getPostUrl(self, lickType, limit, page):
        url = "%s/post.json?limit=%d".format(
            CommonConstant.basicConfig[LickConfig.lickType].get("sourceAddress"),
            limit,
        )
        if lickType == "kch":
            url = url
        elif lickType == "yd":
            url = "%s&login=%s&password_hash=%s".format(
                url,
                LickConfig.extConfig[LickConfig.lickType].get("login"),
                LickConfig.extConfig[LickConfig.lickType].get("password_hash"),
            )
        elif lickType == "wp":
            url = "%s/api/v1/search?apikey=%s&limit=%d".format(
                CommonConstant.basicConfig[LickConfig.lickType].get("sourceAddress"),
                LickConfig.extConfig[LickConfig.lickType].get("api_key"),
                limit,
            )
        else:
            LogUtils.log(f"don't support this type:{lickType} for now..")

        if page > 1:
            url = "%s&page=%d".format(url, page)
        return url

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

    def downloadOnePic(self, img: BaseImgMeta):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.198 Safari/537.36",
            "referer": "https://konachan.com/post",
        }
        # check dir
        downloadPath = CommonConstant.basicConfig[LickConfig.lickType].get(
            "picOutputPath"
        )
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)

        suffix = f".{img.file_ext}"
        filename = f"{downloadPath}/{img.img_id}{suffix}"
        if f"{img.img_id}{suffix}" in historyImgList or os.path.exists(filename):
            print("file id:{0} has exist".format(img.img_id))
            return False

        LogUtils.log(
            f"id:{img.img_id},name:{filename},time:{currentTimeStdFmt()},url:{img.file_url} "
        )

        response = self.httpRetryExecutor(img.file_url, headers)

        LogUtils.log(
            f"begin to write,id:{img.img_id}, time:{currentTimeStdFmt()},path:{filename}"
        )

        if response is None:
            return False

        with open(filename, "xb") as f:
            f.write(response.content)

        LogUtils.log(
            f"end to write,id:{img.img_id},time:{currentTimeStdFmt()},path:{filename} "
        )

        return True

    def downloadPicFromDb(self, subDir=None, start=0, limit=100, maxCount=10000):
        """
        从数据检索图片，并全量下载
        @param subDir:
        @param start:
        @param limit:
        @param maxCount:
        @return:
        """
        # check download path, may create it.
        downloadPath = CommonConstant.basicConfig[LickConfig.lickType].get(
            "picOutputPath"
        )
        if subDir is not None:
            downloadPath = f"{downloadPath}/{subDir}"
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.198 Safari/537.36",
            "referer": CommonConstant.basicConfig[LickConfig.lickType].get(
                "sourceAddress"
            ),
        }

        offset = start
        while True:
            if offset >= maxCount:
                LogUtils.log(f"done all task {offset}")
                break

            val = sqliteManager.selectImgs(limit=limit, offset=offset)
            if val is None or len(val) == 0:
                LogUtils.log(
                    f"download by db data complete, offset:{offset}, start:{start}"
                )
                break
            else:
                LogUtils.log(f"begin to batch download, offset:{offset}, start:{start}")
                for pic in val:
                    suffix = f".{pic.file_ext}"
                    filename = f"{downloadPath}/{pic.img_id}{suffix}"
                    if f"{pic.img_id}{suffix}" in historyImgList or os.path.exists(
                        filename
                    ):
                        continue

                    LogUtils.log(
                        f"begin to download,id:{pic.img_id},name:{filename},time:{currentTimeStdFmt()},url:{pic.file_url}"
                    )

                    response = self.httpRetryExecutor(pic.file_url, headers)
                    if response is None or response.status_code >= 300:
                        LogUtils.log(f"download pic:{filename} failed.")
                        continue

                    LogUtils.log(
                        f"begin to write,id:{pic.img_id}, time:{currentTimeStdFmt()},path:{filename}"
                    )
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    LogUtils.log(
                        f"id:{pic.img_id},time:{currentTimeStdFmt()},path:{filename}"
                    )
            # 更新下一次数据
            offset += limit

    def scrawlPicUseApiAllLatest(self, start_page=1, end_page=1000, start_time=None):
        """
        对外主要函数
        @param start_page:
        @param end_page:
        @param start_time:
        @return:
        """
        currentPage = start_page
        while currentPage < end_page:
            print(
                "{}-begin with scrawl, current page:{}, total page".format(
                    threading.current_thread().name, currentPage
                )
            )
            val = self.scrawlPicUseApi(currentPage, 20, start_time)
            print(
                "{}-end with scrawl, current page:{}, total page".format(
                    threading.current_thread().name, currentPage
                )
            )
            print("..")
            time.sleep(5)
            if val:
                currentPage += 1
            else:
                print(
                    "{}-done with all scrawl, current page:{}".format(
                        threading.current_thread().name, currentPage
                    )
                )
                break
