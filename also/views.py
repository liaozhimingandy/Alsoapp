import time

from django.shortcuts import render
from django.views.generic import View  # 导入类试图
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger  # 数据页面分页使用
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect


# Create your views here.
class DefaultView(View):
    def get(self, request):
        return render(request, "also/index.html")


class ResultView(View):

    @classmethod
    def get(cls, request):
        # print(request.GET.get("q"))
        context = dict()
        context["q"] = request.GET.get("q")
        context["tn"] = request.GET.get("tn")
        if context["q"] is None and context["tn"] is None:
            return HttpResponseRedirect("/")
        tmp_content = {"title": "演示数据", "resume": "来学习一下git log的操作,这个操作是查看git操作的日志,所以,让我们学习一下,为了"
                                                  "更好的讲解这个较为重要的命令行git log,我提前使用git merge featurt.来学习一下git"
                                                  " log的操作,这个操作是查看来学习一下git log的操作,这个操作是查看git操作的日志,所以,"
                                                  "让我们学习一下,为了更git操作的日志,所以,让我们学习一下,为了更", "url": "http://127.0.0.1:8000/"
            , "create_time": time.strftime('%Y-%m-%d', time.localtime(time.time()))
                       }
        content_result_right = [tmp_content for i in range(100)]

        # 数据分页
        paginator = Paginator(content_result_right, 10)  # 页面分页
        try:
            # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
            page = request.GET.get('p')
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
        # print(content_result_right_page)
        context['content_result_right'] = content_result_right_page
        return render(request, "also/result.html", context=context)


class SuggestView(View):
    """搜索建议部分"""

    def get(self, request):
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
