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
            target=kcScrawlImpl.scrawPicUseApiAllLatest,
            args=(1, 20, '2021-05-10 00:00:00'),
            name="FirstThread-1",
        )
        t1.start()

        # 下载图片
        t2 = threading.Thread(
            target=kcScrawlImpl.scrawPicUseApiAllLatest,
            args=(21, 40, '2021-05-10 00:00:00'),
            name="FirstThread-2",
        )
        t2.start()

        # 下载图片
        t3 = threading.Thread(
            target=kcScrawlImpl.scrawPicUseApiAllLatest,
            args=(41, 60, '2021-05-10 00:00:00'),
            name="FirstThread-3",
        )
        t3.start()
        #
        # # 下载图片
        # t4 = threading.Thread(
        #     target=kcScrawlImpl.scrawPicUseApiAllLatest,
        #     args=(301, 400, '2020-11-30 00:00:00'),
        #     name="FirstThread-4",
        # )
        # t4.start()
    except Exception as e:
        print("start thread error.")
        print(e)
