# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2020 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : Alsoapp
#   @File Name   : beta.py
#   @Created Date: 2020-12-20 16:10
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description : 用于测试
#
# ======================================================================

from views import Search


def web_search_beta():
    result = Search.es_search_web(search_wd="date")
    print(result)


def dict_search_beta():
    """字典查询"""
    result = Search.es_search_dict(search_wd="字典")
    print(result)


def main():
    # web_search_beta()
    dict_search_beta()


if __name__ == "__main__":
    main()
