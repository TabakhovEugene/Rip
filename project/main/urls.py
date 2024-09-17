from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home_url'),
    path('habitat/<int:id>/', views.habitat, name='habitat_url'),
    path('basket/<int:id>/', views.basket, name='basket_url'),
    path('search/', views.search, name='search_url'),
]