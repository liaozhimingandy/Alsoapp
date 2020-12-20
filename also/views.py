import time

from django.shortcuts import render
from django.views.generic import View  # 导入类试图
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger  # 数据页面分页使用
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

es = Elasticsearch(['127.0.0.1:9200'])


# Create your views here.
class DefaultView(View):
    def get(self, request):
        return render(request, "also/index.html")


class ResultView(View):

    @classmethod
    def get(cls, request):
        # print(request.GET.get("q"))
        context = dict()
        context["wd"] = request.GET.get("wd")
        context["tn"] = request.GET.get("tn")
        if context["wd"] is None and context["tn"] is None:
            return HttpResponseRedirect("/")

        # todo:限制关键词为40个汉字
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
            es_search_result = Search.es_search_dict(search_wd=search_wd).get("hits")
            content_result_right = list()
            if es_search_result.get('total').get("value", 0) != 0:
                for tmp_data in es_search_result.get("hits"):
                    tmp_content = {"table_name": tmp_data.get('_index'),
                                   "code": tmp_data.get('highlight').get("code")[0] if tmp_data.get('highlight').get(
                                       "code", "") != "" else tmp_data.get("_source").get("code"),
                                   "name": tmp_data.get('highlight').get("name")[0] if tmp_data.get('highlight').get(
                                       "name", "") != "" else tmp_data.get("_source").get("name"),
                                   "desc": tmp_data.get('highlight').get("desc")[0] if tmp_data.get('highlight').get(
                                       "desc", "") != "" else tmp_data.get("_source").get("desc"),
                                   "note": tmp_data.get('highlight').get("note")[0] if tmp_data.get('highlight').get(
                                       "note", "") != "" else tmp_data.get("_source").get("note"),
                                   "create_time": time.strftime('%Y-%m-%d', time.localtime(time.time()))}
                    # print(tmp_data.get('highlight').get("desc"))
                    content_result_right.append(tmp_content)
            # print(content_result_right)
        else:
            es_search_result = Search.es_search_web(search_wd=search_wd).get("hits")
            content_result_right = list()
            if es_search_result.get('total').get("value", 0) != 0:
                for tmp_data in es_search_result.get("hits"):
                    tmp_content = {
                        "title": tmp_data.get('_source').get("title") if tmp_data.get('highlight').get("title",
                                                                                                       "") == "" else
                        tmp_data.get('highlight').get("title")[0],
                        "resume": tmp_data.get('_source').get("desc") if tmp_data.get('highlight').get("desc",
                                                                                                       "") == "" else
                        tmp_data.get('highlight').get("desc")[0],
                        "url": tmp_data.get('_source').get("url"),
                        "create_time": time.strftime('%Y-%m-%d', time.localtime(time.time()))
                    }
                    content_result_right.append(tmp_content)

        end_time = time.time()
        # 查询耗时
        context["result_total_time"] = '{:.3f}'.format(end_time - start_time)
        # 数据分页
        paginator = Paginator(content_result_right, 10)  # 页面分页
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
            return HttpResponse('找不到页面的内容')
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            content_result_right_page = paginator.page(paginator.num_pages)
        context["result_total"] = paginator.count
        context["result_total_format"] = '{:,}'.format(paginator.count)
        context['content_result_right'] = content_result_right_page
        # print(paginator.count)
        if context["tn"] == "dict":
            return render(request, "also/result_dict.html", context=context)
        elif context["tn"] == "also":
            return render(request, "also/result_web.html", context=context)
        elif context["tn"] == "file":
            return render(request, "also/result_web.html", context=context)


class SuggestView(View):
    """搜索建议部分"""

    @classmethod
    def get(cls, request):
        q = request.GET.get("query")
        limit = request.GET.get("limit")
        # sug = [{"label": "中国", "rgb": "(255, 174, 66)", "hex": "#FFAE42"},
        #        {"label": "中华人民共和国", "rgb": "(255, 174, 66)", "hex": "#FFAE42"}]
        sug = [{"label": "中国"}, {"label": "中华人民共和国"}, {"label": "China"}]
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
                "multi_match": {  # 完全匹配搜索关键词，模糊匹配用match
                    "query": search_wd  # 搜索的字段和关键词
                    , "fields": ["title", "desc", "content", "tag"]
                }
            },
            "_source": ["title", "desc", "content", "tag", "url"],
            "highlight": {  # 结果高亮
                "encoder": "html",
                "fields": {
                    "title": {"pre_tags": [
                        "<mark><em class=\"text-danger\">"
                    ],
                        "post_tags": [
                            "</em></mark>"
                        ]},
                    "desc": {
                        "pre_tags": [
                            "<mark><em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em></mark>"
                        ]

                    }

                }
            }
        }
        try:
            search_result = es.search(index="web", body=_query, size=1000, request_timeout=1, ignore=[400, 404],
                                      filter_path=['hits.total', 'hits.hits._index', 'hits.hits._source',
                                                   'hits.hits.highlight',
                                                   'hits.hits._id'])  # index不指定,代表所有索引下进行查找
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
                "multi_match": {  # 完全匹配搜索关键词，模糊匹配用match
                    "query": search_wd  # 搜索的字段和关键词
                    , "fields": ["code", "desc", "note", "name"]
                }
            },
            "_source": ["code", "desc", "note", "name", "offical"],
            "highlight": {  # 结果高亮
                "encoder": "html",
                "fields": {
                    "code": {"pre_tags": [
                        "<mark><em class=\"text-danger\">"
                    ],
                        "post_tags": [
                            "</em></mark>"
                        ]},
                    "desc": {
                        "pre_tags": [
                            "<mark><em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em></mark>"
                        ]
                    },
                    "name": {
                        "pre_tags": [
                            "<mark><em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em></mark>"
                        ]
                    },
                    "note": {
                        "pre_tags": [
                            "<mark><em class=\"text-danger\">"
                        ],
                        "post_tags": [
                            "</em></mark>"
                        ]
                    }
                }
            }
        }
        try:
            search_result = es.search(index="dict", body=_query, size=1000, request_timeout=1, ignore=[400, 404],
                                      filter_path=['hits.total', 'hits.hits._index', 'hits.hits._source',
                                                   'hits.hits.highlight',
                                                   'hits.hits._id'])  # index不指定,代表所有索引下进行查找
        except ConnectionError as e:
            print(e)
            return
        else:
            return search_result
