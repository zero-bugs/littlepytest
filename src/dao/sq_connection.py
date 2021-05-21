#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sqlite3
import threading

from src.config.common_config import CommonConstant
from src.config.lick_config import LickConfig
from src.models.BaseImgMeta import BaseImgMeta


class SqliteManager:
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        """链接数据库，若数据库不存在则创建"""
        self.conn = sqlite3.connect("%s" % CommonConstant.basicConfig[LickConfig.lickType]["dbLibPath"],
                                    check_same_thread=False)
        # 在内存中创建数据库
        # conn = sqlite3.connect(":memory:")
        # 创建游标对象
        self.cur = self.conn.cursor()

        # 创建数据表
        sql = (
            "create table if not exists "
            "tbl_img(img_id integer primary key not null,"
            "width integer,"
            "height integer,"
            "file_size integer,"
            "file_url text,"
            "file_ext text,"
            "tags text,"
            "md5 text,"
            "score integer,"
            "create_at text,"
            "author text,"
            "creator_id text,"
            "img_source text)"
        )
        self.cur.execute(sql)

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SqliteManager, "_instance"):
            with SqliteManager._instance_lock:
                if not hasattr(SqliteManager, "_instance"):
                    SqliteManager._instance = SqliteManager(*args, **kwargs)
        return SqliteManager._instance

    def insertImg(self, pic: BaseImgMeta):
        """插入图片"""
        if pic is None:
            return False

        try:
            lock.acquire(True)
            self.cur.execute(
                "insert or ignore into tbl_img "
                "(img_id,width,height,file_size,file_url,file_ext,tags,md5,score,create_at,author,creator_id,img_source) "
                "values (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    pic.img_id,
                    pic.width,
                    pic.height,
                    pic.file_size,
                    pic.file_url,
                    pic.file_ext,
                    pic.tags,
                    pic.md5,
                    pic.score,
                    pic.create_at,
                    pic.author,
                    pic.creator_id,
                    pic.img_source
                ),
            )
            self.conn.commit()
            return True
        except Exception as err:
            print(err)
            self.conn.rollback()
            return False
        finally:
            lock.release()

    def batchInsertImg(self, pic: list):
        """批量插入图片"""
        if pic is None:
            return False
        elif len(pic) == 0:
            return False
        try:
            for p in pic:
                lock.acquire(True)
                self.cur.execute(
                    "insert or ignore into tbl_img "
                    "(img_id,width,height,file_size,file_url,file_ext,tags,md5,score,create_at,author,creator_id,img_source) "
                    "values (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        pic.img_id,
                        pic.width,
                        pic.height,
                        pic.file_size,
                        pic.file_url,
                        pic.file_ext,
                        pic.tags,
                        pic.md5,
                        pic.score,
                        pic.create_at,
                        pic.author,
                        pic.creator_id,
                        pic.img_source
                    ),
                )
            self.conn.commit()
            return True
        except Exception as err:
            print(err)
            self.conn.rollback()
            return False
        finally:
            lock.release()

    def selectImgs(self, limit=100, offset=0):
        """
        查找指定个数的图片
        """
        result = []
        try:
            lock.acquire(True)
            self.cur.execute("select * from tbl_img limit ? offset ? ", (limit, offset,))
            values = self.cur.fetchall()
            if values is None:
                return None
            for val in values:
                result.append(self.constructImg(val))
            return result
        except Exception as err:
            print(err)
            self.conn.rollback()
            return None
        finally:
            lock.release()

    def selectImgWithId(self, img_id):
        """
        查找指定个数的图片
        """
        try:
            lock.acquire(True)
            self.cur.execute("select * from tbl_img where img_id = ? ", (img_id,))
            val = self.cur.fetchall()
            if val is None:
                return None

            return self.constructImg(val)

        except Exception as err:
            print(err)
            self.conn.rollback()
            return None
        finally:
            lock.release()

    def constructImg(self, val):
        img = BaseImgMeta()
        img.img_id = val[0]
        img.width = val[1]
        img.height = val[2]
        img.file_size = val[3]
        img.file_url = val[4]
        img.file_ext = val[5]
        img.tags = val[6]
        img.md5 = val[7]
        img.score = val[8]
        img.create_at = val[9]
        img.author = val[10]
        img.creator_id = val[11]
        img.img_source = val[12]
        return img

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()


# 创建实例
sqliteManager = SqliteManager()
lock = threading.Lock()
