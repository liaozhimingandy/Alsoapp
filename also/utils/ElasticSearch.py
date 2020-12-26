# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
#   Copyright (C) 2020 liaozhimingandy@qq.com Ltd. All Rights Reserved.
#
#   @Author      : zhiming
#   @Project     : Alsoapp
#   @File Name   : ElasticSearch.py
#   @Created Date: 2020-12-26 18:38
#      @Software : PyCharm
#         @e-Mail: liaozhimingandy@qq.com
#   @Description : ElasticSearch操作类
#
# ======================================================================
import time
import json
from pathlib import Path

# 第三方依赖库
from elasticsearch import Elasticsearch


class ElasticSearch:

    def __init__(self, config_path: list = ["config\config.json"]) -> None:
        # 配置文件
        # config_file = Path(["config", "config.json"])
        paths = config_path
        config = json.loads(Path.cwd().parent.joinpath(*paths).read_text())

        self.es = Elasticsearch(config.get("elasticsearch_cluster"),
                                # 在做任何操作之前，先进行嗅探
                                # sniff_on_start=True,
                                # 节点没有响应时，进行刷新，重新连接
                                sniff_on_connection_fail=True,
                                # 每 60 秒刷新一次
                                # sniffer_timeout=60
                                )

    # 索引file的写入操作
    def es_insert_file(self, file_name, content, file_path, dev_name, size=None, is_directory=False):
        _body = {
            "file_name": file_name,
            "content": content,
            "path": file_path,
            "is_directory": is_directory,
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime()),
            "deleted": False,
            "tags": None,
            "offical": None,
            "dev_name": dev_name,
            "size": size
        }

        result = self.es.index(index="files", body=_body)
        return {"error": 0, "msg": "操作成功", "result": result}


def main():
    es = ElasticSearch()
    # file写入
    es.es_insert_file(file_name="debug.log", content="", file_path=r"D:\tmp\debug.log", dev_name="beta")


if __name__ == "__main__":
    main()
