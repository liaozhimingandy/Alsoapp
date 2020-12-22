# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2020 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : Alsoapp
#   @File Name   : filters.py
#   @Created Date: 2020-12-22 19:53
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description : 过滤器文件
#
# ======================================================================
from django import template

register = template.Library()


@register.filter(name="counter")
def counter(value, page):
    """统计字典模板分页时显示序号"""
    page_size = 10
    return page_size * (page - 1) + value


def main():
    pass


if __name__ == "__main__":
    main()
