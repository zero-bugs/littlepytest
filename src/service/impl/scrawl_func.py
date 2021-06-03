#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import datetime
import json
import os
import time

from src.config.common_config import CommonConstant
from src.config.lick_config import LickConfig

from src.dao.sq_connection import sqliteManager
from src.logs.log_utils import LogUtils
from src.models.base_img_meta import BaseImgMeta
from src.utils.http_utils import getUrlAddress, commonHeaders, httpRetryExecutorWithRetry as httpRequest

historyImgList = list()


def currentTimeStdFmt():
    return time.strftime(CommonConstant.time_format, time.localtime())


class BaseService:
    def __init__(self):
        historyFile = CommonConstant.basicConfig[LickConfig.lickType].get("exportHisList")
        if os.path.exists(historyFile):
            with open(historyFile) as f:
                for line in f.readlines():
                    historyImgList.append(line.strip())
        else:
            LogUtils.log(f"init completed, history file:{historyFile} does not exist.")
        LogUtils.log(f"init completed, history file:{historyFile} count:{len(historyImgList)}")

    def scrawlPicUseApi(self, page=1, limit=100, tags=None):
        """
        首次抓取所有图片存到数据库中
        :param page:页码，第1页不加入url中
        :param limit:单页数量
        :param tags 搜索条件
        :return:
        """
        [url, extParam] = self.getPostUrl(LickConfig.lickType, limit, page, tags)

        LogUtils.log(f"begin to request all images totally, url:{url}")

        resp = httpRequest(url, extParam, commonHeaders, {})
        if resp is None:
            LogUtils.log(f"response is none, url:{url}")
            return False
        elif resp.status_code != 200:
            LogUtils.log(f"url:{url},status code:{resp.status_code}")
            return False

        imgs = list()
        jsonObjs = json.loads(resp.content)
        if LickConfig.lickType == CommonConstant.whType:
            if jsonObjs.get("data") is None or len(jsonObjs.get("data")) == 0:
                LogUtils.log(f"no more images for lick type:{LickConfig.lickType}, url:{url}")
                return [True, page]
            else:
                jsonObjs = jsonObjs.get("data")
        elif jsonObjs is None or len(jsonObjs) == 0:
            LogUtils.log(f"no more images for lick type:{LickConfig.lickType}, url:{url}")
            return [True, page]

        for p in jsonObjs:
            img = self.constructRemoteImg(p)
            imgs.append(img)
        else:
            sqliteManager.batchInsertImg(imgs)
        return True

    def scrawlPicUseApiLatest(self, page=1, limit=100, tags=None, startTime=None):
        """
        首次抓取所有图片存到数据库中
        :param page:
        :param limit:
        :param tags:date:2021-05-01
        :param startTime:startTime="2021-05-01 00:00:00"
        :return:
        """
        [url, extParams] = self.getPostUrl(LickConfig.lickType, limit, page, tags)

        LogUtils.log(f"begin to request latest images from some time, url:{url}")

        resp = httpRequest(url, extParams, commonHeaders, {})
        if resp is None:
            LogUtils.log("response is none, url:%s" % url)
            return False
        elif resp.status_code != 200:
            LogUtils.log("url:%s,status code:%d" % (url, resp.status_code))
            return False

        if startTime is None:
            startTime = datetime.datetime.strptime("1970-01-01 00:00:00", CommonConstant.time_format)
        else:
            startTime = datetime.datetime.strptime(startTime, CommonConstant.time_format)

        imgs = list()
        itemNumsAll = 0
        itemNumsNoNeedDld = 0

        jsonObjs = json.loads(resp.content)
        if jsonObjs is None or len(jsonObjs) == 0:
            LogUtils.log(f"no more images for url:{url}")
            return [True, page]

        for p in jsonObjs:
            itemNumsAll += 1
            img = self.constructRemoteImg(p)
            if datetime.datetime.fromtimestamp(p.get("created_at")) > startTime:
                if self.downloadOnePic(img):
                    imgs.append(img)
                else:
                    LogUtils.log(f"pic:{img.file_url} download failed.")
            else:
                itemNumsNoNeedDld += 1
        else:
            if not sqliteManager.batchInsertImg(imgs):
                LogUtils.log("batch insert images failed.")
                return False
        if itemNumsAll == itemNumsNoNeedDld:
            LogUtils.log("all task done, no new image added...")
        return True

    def constructRemoteImg(self, imgDbObj, lickType=LickConfig.lickType):
        img = BaseImgMeta()
        img.img_id = imgDbObj.get("id")
        img.file_size = imgDbObj.get("file_size")

        if lickType == CommonConstant.kchType or lickType == CommonConstant.ydType:
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
            img.create_at = datetime.datetime.fromtimestamp(imgDbObj.get("created_at")).strftime(
                CommonConstant.time_format
            )
            img.rating = imgDbObj.get("rating")
            img.category = imgDbObj.get("status")
        elif lickType == CommonConstant.whType:
            img.width = imgDbObj.get("dimension_x")
            img.height = imgDbObj.get("dimension_y")
            img.file_url = imgDbObj.get("path")
            img.file_ext = imgDbObj.get("path").split(".")[-1]
            img.score = imgDbObj.get("favorites")
            img.create_at = datetime.datetime.strptime(imgDbObj.get("created_at"), CommonConstant.time_format)
            img.rating = imgDbObj.get("purity")
            img.category = imgDbObj.get("category")
        else:
            LogUtils.log(f"don't support this type:{lickType} for now..")

        return img

    def getPostUrl(self, lickType, limit, page, tags: dict):
        url = f"{getUrlAddress()}"
        extParams = {}
        if lickType == CommonConstant.kchType or lickType == CommonConstant.ydType:
            url = f"{url}/post.json"
            extParams['login'] = LickConfig.extConfig[LickConfig.lickType].get("login")
            extParams['password_hash'] = LickConfig.extConfig[LickConfig.lickType].get("password_hash")
        elif lickType == CommonConstant.whType:
            url = f"{url}/api/v1/search"
            extParams['apikey'] = LickConfig.extConfig[LickConfig.lickType].get("api_key")
        else:
            LogUtils.log(f"don't support this type:{lickType} for now..")

        if tags is not None:
            extParams.update(tags)

        if page > 1:
            extParams['page'] = page
        extParams['limit'] = limit
        return [url, extParams]

    def downloadOnePic(self, img: BaseImgMeta):
        # check dir
        downloadPath = CommonConstant.basicConfig[LickConfig.lickType].get("picOutputPath")
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)

        suffix = f".{img.file_ext}"
        filename = f"{downloadPath}/{img.img_id}{suffix}"
        if f"{img.img_id}{suffix}" in historyImgList or os.path.exists(filename):
            LogUtils.log("file id:{} has exist".format(img.img_id))
            return False

        LogUtils.log(f"id:{img.img_id},name:{filename},time:{currentTimeStdFmt()},url:{img.file_url} ")

        response = httpRequest(img.file_url, {}, commonHeaders, {})

        LogUtils.log(f"begin to write,id:{img.img_id}, time:{currentTimeStdFmt()},path:{filename}")

        if response is None:
            return False

        with open(filename, "xb") as f:
            f.write(response.content)

        LogUtils.log(f"end to write,id:{img.img_id},time:{currentTimeStdFmt()},path:{filename} ")

        return True

    def downloadPicFromDb(self, subDir=None, rating=None, offset=0, limit=100):
        """
        从数据检索图片，并全量下载
        @param subDir:
        @param offset:
        @param limit:
        @param rating:
        @return:
        """
        # check download path, may create it.
        downloadPath = CommonConstant.basicConfig[LickConfig.lickType].get("picOutputPath")
        if subDir is not None:
            downloadPath = f"{downloadPath}/{subDir}"
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)

        val = sqliteManager.selectImgs(rating=None, limit=limit, offset=offset)
        if val is None or len(val) == 0:
            LogUtils.log(f"download by db data complete, offset:{offset}, limit:{limit}")
            return True

        LogUtils.log(f"begin to batch download, offset:{offset}, limit:{limit}")
        for pic in val:
            suffix = f".{pic.file_ext}"
            if LickConfig.lickType == CommonConstant.whType:
                path = f"{downloadPath}/{pic.category}/{pic.rating}"
            else:
                path = f"{downloadPath}/{pic.rating}"

            if not os.path.exists(path):
                os.mkdir(path)

            filename = f"{path}/{pic.img_id}{suffix}"
            if f"{pic.img_id}{suffix}" in historyImgList or os.path.exists(filename):
                continue

            LogUtils.log(
                f"begin to download,id:{pic.img_id},name:{filename},time:{currentTimeStdFmt()},url:{pic.file_url}"
            )

            response = httpRequest(pic.file_url, {}, commonHeaders, {})
            if response is None or response.status_code >= 300:
                LogUtils.log(f"download pic:{filename} failed.")
                continue

            LogUtils.log(f"begin to write,id:{pic.img_id}, time:{currentTimeStdFmt()},path:{filename}")
            with open(filename, "wb") as f:
                f.write(response.content)
            LogUtils.log(f"id:{pic.img_id},time:{currentTimeStdFmt()},path:{filename}")
            time.sleep(0.5)
            return False
