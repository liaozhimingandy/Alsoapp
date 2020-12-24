import time

from django.shortcuts import render
from django.views.generic import View  # 导入类试图
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger  # 数据页面分页使用
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

es = Elasticsearch(['127.0.0.1:9200'])

# 常量分页结果大小
DICT_PAGE_SIZE = 10
WEB_PAGE_SIZE = 10
DEFAULT_PAGE_SIZE = 10


# Create your views here.
class DefaultView(View):
    def get(self, request):
        context = dict()
        # 获取请求者ip地址
        ip = Utils.get_ip(request)
        context["ip"] = ip
        return render(request, "also/index.html", context=context)


class ResultView(View):

    @classmethod
    def get(cls, request):
        context = dict()
        # 获取请求ip
        ip = Utils.get_ip(request)
        context["ip"] = ip
        # 处理含有多个关键词问题
        context["wd"] = "".join(request.GET.getlist("wd"))
        context["tn"] = request.GET.get("tn")
        if any((context["wd"] == "", context["tn"] is None)):
            return HttpResponseRedirect("/")
        # 将用户查询的数据写入search_word表
        Search.es_insert_suggest(sug_word=context["wd"], ip=ip)
        # 限制关键词为40个汉字
        if len(context["wd"].encode("utf8")) >= 80:
            search_wd = context["wd"].encode("utf8")[0:80].decode("utf8")
            context["msg"] = f"\"{search_wd[-3:]}\"及其后面的字词均被忽略，因为我们的查询限制在40个汉字以内"
        else:
            search_wd = context["wd"]
        # 解析因escape编码的数据
        # search_wd = "".join([(len(i) > 0 and chr(int(i, 16)) or "") for i in search_wd.split('%u')])
        context["wd"] = search_wd

        start_time = time.time()
        # elasticsearch查询数据
        if context["tn"] == "dict":
            try:
                es_search_result = Search.es_search_dict(search_wd=search_wd).get("hits")
            except (AttributeError,):
                response = render(request, 'also/500.html', )
                response.status_code = 500
                return response
            else:
                content_result_right = list()
                if es_search_result.get('total').get("value", 0) != 0:
                    for tmp_data in es_search_result.get("hits"):
                        tmp_content = {"table_name": tmp_data.get('_index'),
                                       "code": tmp_data.get('highlight').get("code")[0] if tmp_data.get(
                                           'highlight').get(
                                           "code", "") != "" else tmp_data.get("_source").get("code"),
                                       "name": tmp_data.get('highlight').get("name")[0] if tmp_data.get(
                                           'highlight').get(
                                           "name", "") != "" else tmp_data.get("_source").get("name"),
                                       "desc": tmp_data.get('highlight').get("desc")[0] if tmp_data.get(
                                           'highlight').get(
                                           "desc", "") != "" else tmp_data.get("_source").get("desc"),
                                       "note": tmp_data.get('highlight').get("note")[0] if tmp_data.get(
                                           'highlight').get(
                                           "note", "") != "" else tmp_data.get("_source").get("note"),
                                       "create_time": time.strftime('%Y-%m-%d', time.localtime(time.time()))}
                        # print(tmp_data.get('highlight').get("desc"))
                        content_result_right.append(tmp_content)
            # print(content_result_right)
        elif context["tn"] == "file":
            try:
                es_search_result = Search.es_search_file(search_wd=search_wd).get("hits")
            except (AttributeError,):
                response = render(request, 'also/500.html', )
                response.status_code = 500
                return response
            else:
                content_result_right = list()
                if es_search_result.get('total').get("value", 0) != 0:
                    for tmp_data in es_search_result.get("hits"):
                        tmp_content = {"table_name": tmp_data.get('_index'),
                                       "file_name": tmp_data.get('highlight').get("file_name")[0] if tmp_data.get(
                                           'highlight').get(
                                           "file_name", "") != "" else tmp_data.get("_source").get("file_name"),
                                       "content": tmp_data.get('highlight').get("content")[0] if tmp_data.get(
                                           'highlight').get(
                                           "content", "") != "" else tmp_data.get("_source").get("content"),
                                       "desc": tmp_data.get('highlight').get("desc")[0] if tmp_data.get(
                                           'highlight').get(
                                           "desc", "") != "" else tmp_data.get("_source").get("desc"),
                                       "tags": tmp_data.get('highlight').get("tags")[0] if tmp_data.get(
                                           'highlight').get(
                                           "tags", "") != "" else tmp_data.get("_source").get("tags"),
                                       "path": tmp_data.get('_source').get("path"),
                                       "create_time": tmp_data.get('highlight').get("@timestamp")[0] if tmp_data.get(
                                           'highlight').get(
                                           "@timestamp", "") != "" else tmp_data.get("_source").get("@timestamp")}
                        # print(tmp_data.get('highlight').get("desc"))
                        content_result_right.append(tmp_content)
        else:
            try:
                es_search_result = Search.es_search_web(search_wd=search_wd).get("hits")
            except (AttributeError,):
                response = render(request, 'also/500.html', )
                response.status_code = 500
                return response
            else:
                content_result_right = list()
                if es_search_result.get('total').get("value", 0) != 0:
                    for tmp_data in es_search_result.get("hits"):
                        # print(tmp_data)
                        tmp_content = {
                            "title": tmp_data.get('_source').get("title") if (tmp_data.get(
                                'highlight', "") == "" or tmp_data.get('highlight', "").get("title",
                                                                                            "") == "") else
                            tmp_data.get('highlight').get("title")[0],
                            "resume": tmp_data.get('_source').get("desc") if (tmp_data.get(
                                'highlight', "") == "" or tmp_data.get('highlight').get("desc",
                                                                                        "") == "") else
                            tmp_data.get('highlight').get("desc")[0],
                            # "resume": "北青-北京头条记者提问，近日，美国总统特朗普将美国会此前通过的“外国公司问责法案”签署成法。该法要求加严在美上市外国公司向美国监管机构披露信息的义务。美相关议员表示，该法主要针对中国。中方对此有何评论？",
                            "url": tmp_data.get('_source').get("url"),
                            "create_time": time.strftime('%Y-%m-%d', time.localtime(time.time())),
                            "srcid": tmp_data.get("_id", "null")
                        }
                        content_result_right.append(tmp_content)

        end_time = time.time()
        # 查询耗时
        context["result_total_time"] = '{:.3f}'.format(end_time - start_time)
        # 数据分页
        # 根据参数选择对应的分页大小
        if context["tn"] == "dict":
            paginator = Paginator(content_result_right, DICT_PAGE_SIZE)  # 页面分页
        elif context["tn"] == "also":
            paginator = Paginator(content_result_right, WEB_PAGE_SIZE)  # 页面分页
        elif context["tn"] == "file":
            paginator = Paginator(content_result_right, DEFAULT_PAGE_SIZE)  # 页面分页
        else:
            paginator = Paginator(content_result_right, DEFAULT_PAGE_SIZE)  # 页面分页

        try:
            # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
            page = request.GET.get('pn')
            content_result_right_page = paginator.page(page)
            # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            content_result_right_page = paginator.page(1)
        except InvalidPage:
            # 如果请求的页数不存在, 重定向页面
            # return HttpResponse('找不到页面的内容')
            response = render(request, 'also/404.html', )
            response.status_code = 404
            return response
        except (EmptyPage, Exception):
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            content_result_right_page = paginator.page(paginator.num_pages)

        context["result_total"] = paginator.count
        context["result_total_format"] = '{:,}'.format(paginator.count)
        context['content_result_right'] = content_result_right_page
        # print(paginator.count)

        # 根据参数选择对应的模板
        if context["tn"] == "dict":
            return render(request, "also/result_dict.html", context=context)
        elif context["tn"] == "also":
            return render(request, "also/result_web.html", context=context)
        elif context["tn"] == "file":
            return render(request, "also/result_file.html", context=context)
        else:
            return render(request, "also/result_web.html", context=context)


class SuggestView(View):
    """搜索建议部分"""

    @classmethod
    def get(cls, request):
        sug_wd = request.GET.get("query")
        sug_limit = request.GET.get("limit")
        elasticsearch_result = Search.es_search_suggest(search_wd=sug_wd, search_limit=sug_limit)
        # print(elasticsearch_result)
        # sug = [{"label": "中国", "rgb": "(255, 174, 66)", "hex": "#FFAE42"},
        #        {"label": "中华人民共和国", "rgb": "(255, 174, 66)", "hex": "#FFAE42"}]
        sug = elasticsearch_result.get("result") if elasticsearch_result.get("error") == 0 else [{"label": "搜索一下"}]
        return JsonResponse(sug, safe=False)


def page_not_found(request, exception):
    return render(request, 'also/404.html')


def page_permission_denied(request, exception):
    return render(request, 'also/404.html')


def page_inter_error(request):
    return render(request, 'also/404.html')


class Search:

    @staticmethod
    def es_search_web(search_wd):
        _query = {
            "query": {
                "bool": {
                    "must": [{
                        "multi_match": {  # 完全匹配搜索关键词，模糊匹配用match
                            "query": search_wd  # 搜索的字段和关键词
                            , "fields": ["title", "desc", "content", "tag"]
                        }
                    }, {
                        # 过滤掉已删除的记录
                        'term': {'deleted': 'false'}
                    }
                    ]
                }
            },
            "_source": ["title", "desc", "content", "tag", "url"],
            "highlight": {  # 结果高亮
                "encoder": "html",
                "fields": {
                    "title": {"pre_tags": [
                        "<em class=\"text-danger\">"
                    ],
                        "post_tags": [
                            "</em>"
                        ]},
                    "desc": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]

                    }

                }
            }
        }
        try:
            search_result = es.search(index="web", body=_query, size=1000, request_timeout=1, ignore=[400, 404],
                                      filter_path=['hits.total', 'hits.hits._index', 'hits.hits._source',
                                                   'hits.hits.highlight',
                                                   'hits.hits._id'], scroll='1m')  # index不指定,代表所有索引下进行查找
        except ConnectionError as e:
            # print(e)
            return
        else:
            # print(search_result)
            return search_result

    @staticmethod
    def es_search_dict(search_wd):
        _query = {
            "query": {
                "bool": {
                    "must": [{
                        "multi_match": {  # 完全匹配搜索关键词，模糊匹配用match
                            "query": search_wd  # 搜索的字段和关键词
                            , "fields": ["code", "desc", "note", "name"]
                        }
                    }, {
                        # 过滤掉已删除的记录
                        'term': {'deleted': 'false'}
                    }
                    ]
                }
            },
            "_source": ["code", "desc", "note", "name", "offical"],
            "highlight": {  # 结果高亮
                "encoder": "html",
                "fields": {
                    "code": {"pre_tags": [
                        "<em class=\"text-danger\">"
                    ],
                        "post_tags": [
                            "</em>"
                        ]},
                    "desc": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]
                    },
                    "name": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]
                    },
                    "note": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]
                    }
                }
            }
        }
        try:
            search_result = es.search(index="dict", body=_query, size=1000, request_timeout=1, ignore=[400, 404],
                                      filter_path=['hits.total', 'hits.hits._index', 'hits.hits._source',
                                                   'hits.hits.highlight',
                                                   'hits.hits._id'], scroll='1m')  # index不指定,代表所有索引下进行查找
        except ConnectionError as e:
            print(e)
            return
        else:
            return search_result

    @staticmethod
    def es_search_file(search_wd):
        _query = {
            "query": {
                "bool": {
                    "must": [{
                        "multi_match": {  # 完全匹配搜索关键词，模糊匹配用match
                            "query": search_wd  # 搜索的字段和关键词
                            , "fields": ["file_name", "desc", "content", "tags"]
                        }
                    },
                        {
                            # 过滤掉已删除的记录
                            'term': {'deleted': 'false'}
                        }
                    ]
                }
            },
            "_source": ["file_name", "desc", "content", "tags", "offical", "path", "@timestamp"],
            "highlight": {  # 结果高亮
                "encoder": "html",
                "fields": {
                    "file_name": {"pre_tags": [
                        "<em class=\"text-danger\">"
                    ],
                        "post_tags": [
                            "</em>"
                        ]},
                    "desc": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]
                    },
                    "content": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]
                    },
                    "tags": {
                        "pre_tags": [
                            "<em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em>"
                        ]
                    }
                }
            }
        }
        try:
            search_result = es.search(index="file", body=_query, size=1000, request_timeout=1, ignore=[400, 404],
                                      filter_path=['hits.total', 'hits.hits._index', 'hits.hits._source',
                                                   'hits.hits.highlight',
                                                   'hits.hits._id'], scroll='1m')  # index不指定,代表所有索引下进行查找
        except ConnectionError as e:
            print(e)
            return
        else:
            return search_result

    @staticmethod
    def es_search_suggest(search_wd, search_limit=5):
        _query = {
            "query": {
                "bool": {
                    "must": [{
                        "multi_match": {  # 完全匹配搜索关键词，模糊匹配用match
                            "query": search_wd  # 搜索的字段和关键词
                            , "fields": ["word"]
                        }
                    }],
                    # 查询后进行过滤
                    'filter': [
                        {'term': {'deleted': 'true'}}
                    ]
                }
            },
            "_source": ["word", "count"],
            "sort": [
                {"count": "desc"}
            ]
        }
        try:
            search_result = es.search(index="search_wd", body=_query, size=search_limit, request_timeout=1,
                                      ignore=[400, 404],
                                      filter_path=['hits.total', 'hits.hits._index', 'hits.hits._source',
                                                   'hits.hits.highlight',
                                                   'hits.hits._id'], scroll='1m')  # index不指定,代表所有索引下进行查找
        except ConnectionError as e:
            return {"error": 1, "msg": e}
        else:
            if search_result.get("hits").get("total").get("value", 0) > 0:
                list_sug = list()
                for tmp_data in search_result.get("hits").get("hits"):
                    list_sug.append(
                        {"label": tmp_data.get("_source").get("word"), "count": tmp_data.get("_source").get("count")})
            else:
                list_sug = [{"label": "搜索一下"}]
            return {"error": 0, "msg": "查询成功!", "result": list_sug}

    @staticmethod
    def es_query_suggest(search_wd):
        _body = {
            "query": {
                "term": {
                    "word": search_wd
                }
            }
        }
        # todo: 完善用户搜索时写入数据库操作
        result = es.search(index="search_word", body=_body, filter_path=["hits.hits._id", "hits.hits._source"])
        # if result.get("hits").get("total").get("value", 0) > 0:

        return {"error": 0, "msg": "查询成功!", "result": result.get("hits").get("hits")}

    @staticmethod
    def es_insert_suggest(sug_word, ip):
        _body = {
            "word": sug_word,
            "@ip": ip,
            "timestamp": None,
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime()),
            "count": 1,
            "tags": ["百度", "实时"],
            "deleted": False
        }

        result = es.index(index="search_word", body=_body)
        es_query = Search.es_query_suggest(search_wd=sug_word)
        print(es_query)
        print(result)


class Utils:
    """工具类"""

    # X-Forwarded-For:简称XFF头，它代表客户端，也就是HTTP的请求端真实的IP，只有在通过了HTTP 代理或者负载均衡服务器时才会添加该项。
    @staticmethod
    def get_ip(request):
        """获取请求者的IP信息"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
        return ip
