"""Alsoapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import DefaultView, ResultView, SuggestView

# 应用命名空间
app_name = "alsoapp"

urlpatterns = [
    path('', DefaultView.as_view(), name="default"),
    path('s', ResultView.as_view(), name="result"),
    path("sug", SuggestView.as_view(), name="suggest"),
]
