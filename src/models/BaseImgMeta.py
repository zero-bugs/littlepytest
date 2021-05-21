#!/usr/bin/python3
# -*- coding: UTF-8 -*-


class BaseImgMeta:
    """image attribute"""

    def __init__(self):
        self.img_id = "00000"
        self.width = 0
        self.height = 0
        self.file_size = 0
        self.file_url = ""
        self.file_ext = ""
        self.tags = ""
        self.md5 = ""
        self.score = 0
        self.create_at = ""
        self.author = ""
        self.creator_id = ""
        self.img_source = ""

