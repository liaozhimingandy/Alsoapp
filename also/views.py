from django.shortcuts import render
from django.views.generic import View  # 导入类试图


# Create your views here.
class DefaultView(View):
    def get(self, request):
        return render(request, "also/index.html")


class ResultView(View):
    def get(self, request):
        print(request.GET.get("q"))
        context = dict()
        context["q"] = request.GET.get("q")
        return render(request, "also/result.html", context=context)


class SuggestView(View):
    """搜索建议部分"""
    def get(self, request):
        q = request.GET.get("query")
        limit = request.GET.get("limit")
        # sug = [{"label": "中国", "rgb": "(255, 174, 66)", "hex": "#FFAE42"},
        #        {"label": "中华人民共和国", "rgb": "(255, 174, 66)", "hex": "#FFAE42"}]
        sug = [{"label": "中国"}, {"label": "中华人民共和国"}, {"label": "China"}]
        from django.http import JsonResponse
        return JsonResponse(sug, safe=False)