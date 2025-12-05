# api/urls.py
from django.urls import path
from .views import  PubMedArticlesView

urlpatterns = [
    path('articles/', PubMedArticlesView.as_view(), name='pubmed-articles'),
]

