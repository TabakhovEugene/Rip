from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home_url'),
    path('habitat/<int:id>/', views.habitat, name='habitat_url'),
    path('basket/<int:id>/', views.basket, name='basket_url'),
    path('add-habitat/', views.add_habitat, name='add_habitat'),
    path('del-animal/', views.del_animal, name='del_animal'),
]