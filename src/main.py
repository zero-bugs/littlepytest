#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import threading

from src.service.impl.scrawl_service import ScrawlServiceImpl

if __name__ == "__main__":
    # 第一阶段api提取数据
    service = ScrawlServiceImpl()

    try:
        # 下载图片
        t1 = threading.Thread(
            target=service.scrawlPicUseApiAll,
            args=(1, 200, 500, "date:..2021-05-23"),
            name="FirstThread-1",
        )
        t1.start()

        t2 = threading.Thread(
            target=service.scrawlPicUseApiAll,
            args=(200, 400, 500, "date:..2021-05-23"),
            name="FirstThread-2",
        )
        t2.start()

        t3 = threading.Thread(
            target=service.scrawlPicUseApiAll,
            args=(400, 600, 500, "date:..2021-05-23"),
            name="FirstThread-2",
        )
        t3.start()
    except Exception as e:
        print("start thread error.")
        print(e)
