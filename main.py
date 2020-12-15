#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import threading

from common.common_config import CommonConstant
from func.kc_scrawl import KcScrawlImpl, historyImgList

if __name__ == "__main__":
    # 第一阶段api提取数据
    kcScrawlImpl = KcScrawlImpl()
    kcScrawlImpl.init()
    # kcScrawlImpl.scrawPicUseApiAll()

    print(len(historyImgList))

    try:
        # 下载图片
        t1 = threading.Thread(
            target=kcScrawlImpl.downloadPicFromDb,
            args=(46500, 50000, f"{CommonConstant.picOutputPath}/1"),
            name="FirstThread-1",
        )
        t1.start()

        # 下载图片
        t2 = threading.Thread(
            target=kcScrawlImpl.downloadPicFromDb,
            args=(133000, 150000, f"{CommonConstant.picOutputPath}/2"),
            name="SecondThread-1",
        )
        t2.start()

        # 下载图片
        t3 = threading.Thread(
            target=kcScrawlImpl.downloadPicFromDb,
            args=(85000, 100000, f"{CommonConstant.picOutputPath}/3"),
            name="ThirdThread-1",
        )
        t3.start()

        # 下载图片
        t4 = threading.Thread(
            target=kcScrawlImpl.downloadPicFromDb,
            args=(179000, 200000, f"{CommonConstant.picOutputPath}/4"),
            name="ForthThread-1",
        )
        t4.start()

    except Exception as e:
        print("start thread error.")
        print(e)
