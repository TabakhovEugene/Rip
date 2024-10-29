from django.contrib import admin
from animals import views
from django.urls import include, path
from rest_framework import routers

from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    path('admin/', admin.site.urls),

    # Услуги
    path(r'habitats/', views.HabitatList.as_view(), name='habitats-list'),  # список мест обитания (GET),

    path(r'habitats/<int:pk>/', views.HabitatDetail.as_view(), name='habitat-detail'),  # получить место обитания (GET),
    path(r'habitats/create/', views.HabitatDetail.as_view(), name='habitat-create'),  # добавление места обитания (POST),
    path(r'habitats/update/<int:pk>/', views.HabitatDetail.as_view(), name='habitat-update'), # редактирование места обитания (PUT),
    path(r'habitats/delete/<int:pk>/', views.HabitatDetail.as_view(), name='habitat-delete'), # удаление места обитания (DELETE),

    path(r'habitats/add/<int:pk>/', views.AddHabitatView.as_view(), name='add-habitat-to-animal'), # добавление МО в заявку (POST),

    path(r'habitats/image/', views.ImageView.as_view(), name='add-image'),  # замена изображения

    # Заявки
    path(r'list-animals/', views.ListAnimals.as_view(), name='list-animals-by-username'), # получить заявки (GET),
    path(r'animal/<int:pk>/', views.GetAnimal.as_view(), name='get-animal-by-id'), # получить конкретную заявку (GET),
    path(r'animal/<int:pk>/', views.GetAnimal.as_view(), name='put-animal-by-id'), # изменить конкретную заявку (PUT),

    path(r'form-animal/<int:pk>/', views.FormAnimal.as_view(), name='form-animal-by-id'), #формирование заявки (PUT)
    path(r'moderate-animal/<int:pk>/', views.ModerateAnimal.as_view(), name='moderate-animal-by-id'), #завершить/отклонить модератором (PUT)
    path(r'delete-animal/<int:pk>/', views.ModerateAnimal.as_view(), name='delete-animal-by-id'), #удалить заявку (DELETE)

    # m-m
    path(r'delete-from-animal/<int:animal_pk>/habitat/<int:habitat_pk>/', views.EditAnimalHabitat.as_view(), name='delete-from-animal-by-id'), #удалить из заявки (DELETE)
    path(r'add-population-to-animal/<int:animal_pk>/habitat/<int:habitat_pk>/', views.EditAnimalHabitat.as_view(), name='add-population-request-by-id'),

    # Users
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserUpdateView.as_view(), name='profile'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]
