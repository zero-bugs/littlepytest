# !/usr/bin/python3
# -*- coding: UTF-8 -*-
import os

from src.config.common_config import CommonConstant
from src.config.lick_config import LickConfig


def get_file_list(dir_name):
    file_list = list()
    for home, dirs, filenames in os.walk(dir_name):
        print(f"home:{home}, dirs:{dirs}")
        for pt in dirs:
            print(pt)

        for filename in filenames:
            filename = filename.strip()
            if filename.startswith("wallhaven-"):
                filename = filename.split("-")[-1]
            file_list.append(filename)
    return file_list


if __name__ == "__main__":
    src = CommonConstant.basicConfig[LickConfig.lickType].get("picOutputPath")
    files = get_file_list(src)
    output = CommonConstant.basicConfig[LickConfig.lickType].get("exportHisList")
    with open(output, mode="w") as f:
        f.writelines("\n".join(files))
