#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import threading

from common.common_config import CommonConstant
from models.pic_attr import PicAttr


class SqliteManager:
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        # 链接数据库，若数据库不存在则创建
        self.conn = sqlite3.connect("%s" % CommonConstant.dbLibPath)
        # 在内存中创建数据库
        # conn = sqlite3.connect(":memory:")
        # 创建游标对象
        self.cur = self.conn.cursor()

        # 创建数据表
        sql = (
            "create table if not exists "
            "fullimgtable(id integer primary key not null,"
            "width integer,"
            "height integer,"
            "filesize integer,"
            "score integer,"
            "md5 text,"
            "preview_url text,"
            "file_url text,"
            "tags text,"
            "create_at integer,"
            "creator_id text,"
            "source text)"
        )
        self.cur.execute(sql)

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SqliteManager, "_instance"):
            with SqliteManager._instance_lock:
                if not hasattr(SqliteManager, "_instance"):
                    SqliteManager._instance = SqliteManager(*args, **kwargs)
        return SqliteManager._instance

    def insertImg(self, pic: PicAttr):
        if pic is None:
            return False

        try:
            self.cur.execute(
                "insert or ignore into fullimgtable (id,width,height,filesize,score,md5,preview_url,file_url,tags,create_at,creator_id,source) values (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    pic.id,
                    pic.width,
                    pic.height,
                    pic.file_size,
                    pic.score,
                    pic.md5,
                    pic.previewUrl,
                    pic.fileUrl,
                    pic.tags,
                    pic.create_at,
                    pic.creator_id,
                    pic.source,
                ),
            )
            self.conn.commit()
            return True
        except Exception as err:
            print(err)
            self.conn.rollback()
            return False

    def batchInsertImg(self, pic: list[PicAttr]):
        if pic is None:
            return False
        elif len(pic) == 0:
            return False
        try:
            for p in pic:
                self.cur.execute(
                    "insert or ignore into fullimgtable (id,width,height,filesize,score,md5,preview_url,file_url,tags,create_at,creator_id,source) values (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        p.id,
                        p.width,
                        p.height,
                        p.file_size,
                        p.score,
                        p.md5,
                        p.previewUrl,
                        p.fileUrl,
                        p.tags,
                        p.create_at,
                        p.creator_id,
                        p.source,
                    ),
                )
            self.conn.commit()
            return True
        except Exception as err:
            print(err)
            self.conn.rollback()
            return False

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()


sqliteManager = SqliteManager()
