#!/usr/bin/python
# -*- coding: UTF-8 -*-
from db.sq_connection import SqliteManager, sqliteManager
from func.kc_scrawl import KcScrawlImpl
from models.pic_attr import PicAttr

if __name__ == "__main__":
    kcScrawlImpl = KcScrawlImpl()
    kcScrawlImpl.scrawPicUseApiAll()
