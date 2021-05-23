#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sqlite3
import threading

from src.config.common_config import CommonConstant
from src.config.lick_config import LickConfig
from src.logs.log_utils import LogUtils
from src.models.base_img_meta import BaseImgMeta


def mapImgToList(imgs: BaseImgMeta):
    if imgs is None:
        return list()

    result = list()
    for img in imgs:
        cLst = list()
        cLst.append(img.img_id),
        cLst.append(img.width),
        cLst.append(img.height),
        cLst.append(img.file_size),
        cLst.append(img.file_url),
        cLst.append(img.file_ext),
        cLst.append(img.tags),
        cLst.append(img.md5),
        cLst.append(img.score),
        cLst.append(img.create_at),
        cLst.append(img.author),
        cLst.append(img.creator_id),
        cLst.append(img.img_source),
        cLst.append(img.rating),
        result.append(cLst)
    else:
        return result


class SqliteManager:
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        """链接数据库，若数据库不存在则创建"""
        dbPath = CommonConstant.basicConfig[LickConfig.lickType]["dbLibPath"]
        LogUtils.log(f"db path:{dbPath}, current path:{os.path.abspath('.')}")
        self.conn = sqlite3.connect(dbPath, check_same_thread=False)
        # 在内存中创建数据库
        # conn = sqlite3.connect(":memory:")
        # 创建游标对象
        self.cur = self.conn.cursor()

        # 创建数据表
        sql = (
            "create table if not exists "
            "tbl_img(img_id VARCHAR(20) primary key not null ,"
            "width integer,"
            "height integer,"
            "file_size integer,"
            "file_url text,"
            "file_ext text,"
            "tags text,"
            "md5 text,"
            "score integer,"
            "create_at datetime,"
            "author text,"
            "creator_id text,"
            "img_source text,"
            "rating text)"
        )
        self.cur.execute(sql)

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SqliteManager, "_instance"):
            with SqliteManager._instance_lock:
                if not hasattr(SqliteManager, "_instance"):
                    SqliteManager._instance = SqliteManager(*args, **kwargs)
        return SqliteManager._instance

    def insertImg(self, img: BaseImgMeta):
        """插入图片"""
        if img is None:
            return False

        try:
            lock.acquire(True)
            self.cur.execute(
                "insert or ignore into tbl_img "
                "(img_id,width,height,file_size,file_url,file_ext,tags,md5,score,create_at,author,creator_id,img_source,rating) "
                "values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    img.img_id,
                    img.width,
                    img.height,
                    img.file_size,
                    img.file_url,
                    img.file_ext,
                    img.tags,
                    img.md5,
                    img.score,
                    img.create_at,
                    img.author,
                    img.creator_id,
                    img.img_source,
                ),
            )
            self.conn.commit()
            return True
        except Exception as err:
            LogUtils.log(err)
            self.conn.rollback()
            return False
        finally:
            lock.release()

    def batchInsertImg(self, imgs: list):
        """批量插入图片"""
        if imgs is None:
            return False
        elif len(imgs) == 0:
            return False
        try:
            lock.acquire(True)
            self.cur.executemany(
                "insert or ignore into tbl_img "
                "(img_id,width,height,file_size,file_url,file_ext,tags,md5,score,create_at,author,creator_id,img_source,rating) "
                "values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                mapImgToList(imgs),
            )
            self.conn.commit()
            return True
        except Exception as err:
            LogUtils.log(err)
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
            self.cur.execute(
                "select * from tbl_img limit ? offset ? ",
                (
                    limit,
                    offset,
                ),
            )
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
        img.rating = val[13]
        return img

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()


# 创建实例
sqliteManager = SqliteManager()
lock = threading.Lock()
