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
