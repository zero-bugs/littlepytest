#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import time
from random import random

from src.logs.log_utils import LogUtils
from src.service.impl.scrawl_func import BaseService


class ScrawlServiceImpl:
    @staticmethod
    def scrawlPicUseApiAllLatest(startPage=1, endPage=1000, limit=10, tags=None):
        """
        对外主要API接口，获取最新图片
        :param startPage:
        :param endPage:
        :param limit:
        :param tags:
        :return:
        """
        LogUtils.log(
            f"begin to scrawl latest image, start page:{startPage}, end page:{endPage}, limit:{limit}, tags:{tags}"
        )
        currentPage = startPage
        service = BaseService()
        while currentPage <= endPage:
            LogUtils.log(
                f"begin with scrawl, current page:{currentPage}, end page:{endPage}, limit:{limit}, tags:{tags}"
            )
            val = service.scrawlPicUseApiLatest(currentPage, limit, tags)
            LogUtils.log(f"end with scrawl, current page:{currentPage}, end page:{endPage}, limit:{limit}, tags:{tags}")
            print("...")
            time.sleep(1)
            if isinstance(val, list) and len(val) == 2:
                LogUtils.log(f"done with all scrawl, current page:{currentPage}")
                break
            else:
                currentPage += 1
        LogUtils.log(f"All task done, current page:{currentPage}, end page:{endPage}, tags:{tags}")

    @staticmethod
    def scrawlPicUseApiAll(startPage=1, endPage=1000, limit=200, tags=None):
        """
        对外主要API接口，首次获取所有图片数据并存入数据库
        :param startPage:
        :param endPage:
        :param limit:
        :param tags:
        :return:
        """
        time.sleep(random() * 5)
        currentPage = startPage
        service = BaseService()
        while currentPage <= endPage:
            LogUtils.log(
                f"begin with scrawl, current page:{currentPage}, end page:{endPage}, limit:{limit}, tags:{tags}"
            )
            val = service.scrawlPicUseApi(currentPage, limit, tags)
            LogUtils.log(f"end with scrawl, current page:{currentPage}, end page:{endPage}, limit:{limit}, tags:{tags}")
            print("...")
            time.sleep(5)
            if isinstance(val, list) and len(val) == 2:
                LogUtils.log(f"done with all scrawl, current page:{currentPage}")
                break
            else:
                currentPage += 1
        LogUtils.log(f"all task done, current page:{currentPage}, end page:{endPage}")

    @staticmethod
    def downloadImagesUseLocalDb(startPage=0, endPage=100, limit=100, subDir=None, rating=None):
        """
        对外主要API接口，使用本地数据库中的数据下载图片
        :param rating:
        :param startPage:
        :param endPage:
        :param limit:
        :param subDir:
        :return:
        """
        time.sleep(random() * 5)
        service = BaseService()
        offset = startPage * limit
        while True:
            if startPage > endPage:
                LogUtils.log(f"done all task, current page:{startPage}, end page:{endPage}, offset:{offset}")
                break

            LogUtils.log(f"begin to download, current page:{startPage}, end page:{endPage}, offset:{offset}")
            if service.downloadPicFromDb(subDir, rating, offset, limit):
                LogUtils.log(f"db is empty, done, current page:{startPage}, end page:{endPage}, offset:{offset}")
                break

            LogUtils.log(f"end to download, current page:{startPage}, end page:{endPage}, offset:{offset}")
            # 更新下一次数据
            offset += limit
            startPage += 1
