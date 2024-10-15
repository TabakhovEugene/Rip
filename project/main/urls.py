from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home_url'),
    path('habitat/<int:id>/', views.habitat, name='habitat_url'),
    path('animal/<int:id>/', views.animal, name='animal_url'),
    path('add-habitat/', views.add_habitat, name='add_habitat'),
    path('del-animal/', views.del_animal, name='del_animal'),
]