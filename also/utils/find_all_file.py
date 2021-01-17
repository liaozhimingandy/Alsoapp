# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2020 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : Alsoapp
#   @File Name   : find_all_file.py
#   @Created Date: 2020-12-26 16:33
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description : 遍历指定目录下所有文件
#
# ======================================================================

import os
import json
from pathlib import Path

# 日志打印
from loguru import logger

from ElasticSearch import ElasticSearch

# 配置文件
# config_file = Path(["config", "config.json"])
paths = ["..", "config", "config.json"]


class DocSpider:

    # 初始化
    def __init__(self) -> None:
        # super(DocSpider, self).__init__()
        self.__config = json.loads(Path.cwd().joinpath(*paths).read_text())
        self.__name = "DocSpider"
        self.__es = ElasticSearch()

    # 遍历所有文件
    def find_all_file(self, dir_file):
        count_file, count_dir = 0, 0
        for dir_path, dirs, files in os.walk(dir_file):
            """
            dirpath 是一个string，代表目录的路径，
            dirs 是一个list，包含了dirpath下所有子目录的名字。
            filenames 是一个list，包含了非目录文件的名字,
            排除配置文件config.json中指定的目录
            """
            filter_file = self.__config.get("filter_dir", [])
            dirs[:] = [d for d in set(dirs) - set(filter_file)]
            # "采集指定目录下的文件"
            # filter_file = ["BaiduNetdiskDownload"]
            # dirs[:] = [d for d in set(filter_file)]
            # 不再对文件目录进行索引
            # for _dir in dirs:
            #     tmp_file_path = os.path.join(dir_path, _dir)
            #     dev_name = os.popen("hostname").read()
            #     is_directory = True
            # print(tmp_file_path)
            # 写入到es数据库
            # es.es_insert_file(file_name=_dir, content=None, file_path=tmp_file_path, dev_name=dev_name,
            #                   is_directory=is_directory)
            # count_dir += 1
            # 常见文件后缀名格式配置文件:文件config.json
            suffix_file = set(self.__config.get("file_suffixes", []))
            # 遍历该目录下的所有文件
            for file in files:
                # 获取文件后缀名
                suffix = os.path.splitext(file)[-1]
                if suffix.lower() not in suffix_file:
                    continue
                tmp_file_path = os.path.join(dir_path, file).replace("\n", "")
                file_stat_info = os.stat(tmp_file_path)
                tmp_file_size = self.str_of_size(file_stat_info.st_size)
                tmp_file_content = None
                dev_name = os.popen("hostname").read()
                is_directory = False
                if file.endswith(".txt"):
                    with open(tmp_file_path) as f:
                        try:
                            tmp_file_content = f.readlines()
                        except Exception as e:
                            print(e)
                            tmp_file_content = None
                # print(f"文件名称:{file},文件路径:{tmp_file_path}, 文件路径:{tmp_file_size}")
                # 写入到es数据库
                self.__es.es_insert_file(file_name=file, content=tmp_file_content, file_path=tmp_file_path,
                                         size=tmp_file_size, dev_name=dev_name, is_directory=is_directory)
                count_file += 1
                logger.info(f"完成第{count_file}文件收录!(文件名称:{file})")
            count_dir += 1
            # break
        print(f"共记录到{count_file}个文件,遍历了{count_dir}个目录!")

    # 文件数据大小单位转换
    @classmethod
    def str_of_size(cls, file_size: int) -> str:
        """
        递归实现，精确为最大单位值 + 小数点后两位
        :param file_size:文件原始大小单位是字节B
        :return:
        """
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024
        for unit in units:
            if (file_size / size) < 1:
                return "{:.2f}{}".format(file_size, unit)
            file_size = file_size / size

    # 遍历所有盘符
    def loop_disk(self):
        # 遍历所有盘符C: 65
        for t in range(68, 91):
            drive_name = chr(t) + ":\\"
            if os.path.isdir(drive_name):
                self.find_all_file(dir_file=drive_name)


def main():
    finder = DocSpider()
    finder.loop_disk()


if __name__ == "__main__":
    main()
    # print(DocSpider.str_of_size(26107904))
