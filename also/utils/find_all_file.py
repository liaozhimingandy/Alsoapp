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

from utils.ElasticSearch import ElasticSearch


# 文件数据大小单位转换
def str_of_size(file_size):
    """
    递归实现，精确为最大单位值 + 小数点后三位
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (file_size / size) < 1:
            return "{:.2f}{}".format(file_size, units[i])
        file_size = file_size / size


# 遍历所有文件
def find_all_file(dir_file):
    count_file = 0
    es = ElasticSearch()
    for dir_path, dirs, files in os.walk(dir_file):
        """
        dirpath 是一个string，代表目录的路径，
        dirs 是一个list，包含了dirpath下所有子目录的名字。
        filenames 是一个list，包含了非目录文件的名字
        """
        # 排除.git下的文件
        if not filter_file_pass(dir_path):
            continue

        for _dir in dirs:
            tmp_file_path = f"{dir_path}\\{_dir}"
            dev_name = os.popen("hostname").read()
            is_directory = True
            print(tmp_file_path)
            # 写入到es数据库
            es.es_insert_file(file_name=_dir, content=None, file_path=tmp_file_path, dev_name=dev_name,
                              is_directory=is_directory)

        # 遍历该目录下的所有文件
        for file in files:
            # 过滤不需要的文件
            if not filter_file_pass(file):
                continue
            tmp_file_path = f"{dir_path}\\{file}"
            file_stat_info = os.stat(tmp_file_path)
            # print(f"文件名称:{file},文件路径:{tmp_file_path}, 文件路径:{str_of_size(file_stat_info.st_size)}")
            tmp_file_size = str_of_size(file_stat_info.st_size)
            tmp_file_content = None
            if file.endswith(".log"):
                with open(tmp_file_path) as f:
                    tmp_file_content = f.readlines()
            dev_name = os.popen("hostname").read()
            is_directory = False
            size = str_of_size(file_stat_info.st_size)
            print(file)
            # print(str_of_size(file_stat_info.st_size))
            # print(file_stat_info.st_type)
            # print(file_stat_info.st_ctime)
            # 写入到es数据库
            es.es_insert_file(file_name=file, content=tmp_file_content, file_path=tmp_file_path, size=size,
                              dev_name=dev_name,
                              is_directory=is_directory)
            count_file += 1
        # break
    print(f"共写入{count_file}条数据!")


# 过滤用户自定义的文件或目录
def filter_file_pass(file: str = "") -> bool:
    filter_file = [".git", ".idea", "$RECYCLE", ".kgtemp", ".cfg", ".krc", ".tmp", ".dll"]
    for tmp_filter in filter_file:
        if file.find(tmp_filter) >= 0:
            return False
        if file.startswith("$"):
            return False
    return True


def main():
    base = r"D:\\"
    find_all_file(base)
    # print(filter_file_pass(base))


if __name__ == "__main__":
    main()
