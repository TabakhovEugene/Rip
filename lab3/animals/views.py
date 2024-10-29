from django.db.models import F

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import *
from .models import Animal, Habitat, HabitatAnimal
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from django.contrib.auth import login
from datetime import datetime

from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class HabitatList(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    model_class = Habitat
    serializer_class = HabitatListSerializer

    # получить список мест обитаний

    @swagger_auto_schema(
        operation_description="Получение списка мест обитания. Можно отфильтровать по его названию.",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Название места обитания",
                              type=openapi.TYPE_STRING, default=""),
        ],
        responses={200: HabitatListSerializer(many=True)}
    )

    def get(self, request):
        if 'title' in request.GET:
            habitats = self.model_class.objects.filter(title__icontains=request.GET['title'])
        else:
            habitats = self.model_class.objects.all()

        serializer = self.serializer_class(habitats, many=True)
        resp = serializer.data
        if Animal.objects.filter(user=request.user, status='draft').exists():
            draft_request = Animal.objects.filter(user=request.user, status='draft').first()
            draft_request_id = Animal.objects.filter(user=request.user, status='draft').first().id
            count_habitats_in_draft = HabitatAnimal.objects.filter(animal=draft_request).values_list('habitat_id', flat=True).count()
            if draft_request:
                resp.append({'draft_request_id': draft_request_id})
                resp.append({'count': count_habitats_in_draft})
        else:
            resp.append({'draft_request_id': None})
            resp.append({'count': 0})

        return Response(resp, status=status.HTTP_200_OK)


class HabitatDetail(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    model_class = Habitat
    serializer_class = HabitatDetailSerializer

    @swagger_auto_schema(
        operation_description="Получить информацию о конкретном месте обитания по ID.",
        responses={200: HabitatDetailSerializer()}
    )
    # получить место обитания
    def get(self, request, pk):
        habitat = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(habitat)
        return Response(serializer.data)

    # удалить место обитания (для модератора)
    @swagger_auto_schema(
        operation_description="Удаление места обитания по ID (moderators only).",
        responses={204: 'No Content', 403: 'Forbidden'}
    )
    def delete(self, request, pk):

        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        habitat = get_object_or_404(self.model_class, pk=pk)
        habitat.status = 'deleted'
        habitat.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # добавить новое место обитания (для модератора)
    @swagger_auto_schema(
        operation_description="Добавление нового МО (moderators only).",
        request_body=HabitatDetailSerializer,
        responses={201: HabitatDetailSerializer(), 400: 'Bad Request'}
    )
    def post(self, request, format=None):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # обновление места обитания (для модератора)
    @swagger_auto_schema(
        operation_description="Обновление данных МО (moderators only).",
        request_body=HabitatDetailSerializer,
        responses={200: HabitatDetailSerializer(), 400: 'Bad Request'}
    )
    def put(self, request, pk, format=None):

        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        habitat = get_object_or_404(self.model_class, id=pk)
        serializer = self.serializer_class(habitat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddHabitatView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    # добавление услуги в заявку
    @swagger_auto_schema(
        operation_description="Добавление МО в заявку-черновик пользователя. Создается новая заявка, если не существует заявки-черновика",
        responses={200: "МО успешно добавлено в заявку", 404: "МО не найдено"},
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Номер места обитания", type=openapi.TYPE_INTEGER,
                              required=True)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'population': openapi.Schema(type=openapi.TYPE_NUMBER, description='Популяция в данном МО', example=10000)},
            required=[]
        )
    )
    def post(self, request, pk):
        # создаем заявку, если ее еще нет
        if not Animal.objects.filter(user=request.user, status='draft').exists():
            new_animal = Animal()
            new_animal.user = request.user
            new_animal.username = request.user.username
            new_animal.save()
        # else:
        #     new_animal = Animal.objects.filter(user=request.user, status='draft')

        animal_id = Animal.objects.filter(user=request.user, status='draft').first().id
        # serializer = AnimalHabitatSerializer(data=request.data)
        if Habitat.objects.filter(pk=pk).exists():
            new_animal_habitat = HabitatAnimal()
            new_animal_habitat.habitat_id = pk
            new_animal_habitat.animal_id = animal_id
            if 'population' in request.data:
                new_animal_habitat.population = request.data["population"]
            new_animal_habitat.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error':'threat not found'}, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    def process_file_upload(self, file_object: InMemoryUploadedFile, client, image_name):
        try:
            client.put_object('static', image_name, file_object, file_object.size)
            return f"http://localhost:9000/static/{image_name}"
        except Exception as e:
            return {"error": str(e)}

    def add_pic(self, habitat, pic):
        client = Minio(
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
        )
        i = habitat.id
        img_obj_name = f"{i}.png"

        if not pic:
            return Response({"error": "Нет файла для изображения логотипа."})
        result = self.process_file_upload(pic, client, img_obj_name)

        if 'error' in result:
            return Response(result)

        habitat.img_url = result
        habitat.save()

        return Response({"message": "success"})

    @swagger_auto_schema(
        operation_description="Upload an image for a specific threat.",
        request_body=AddImageSerializer,
        responses={201: "Image uploaded successfully", 400: "Bad request"}
    )
    def post(self, request):
        if not request.user.is_staff:
           return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AddImageSerializer(data=request.data)
        if serializer.is_valid():
            habitat = Habitat.objects.get(pk=serializer.validated_data['habitat_id'])
            pic = request.FILES.get("pic")
            pic_result = self.add_pic(habitat, pic)
            # Если в результате вызова add_pic результат - ошибка, возвращаем его.
            if 'error' in pic_result.data:
                return pic_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Личный кабинет (обновление профиля)
class UserUpdateView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Обновление профиля аунтифицированного пользователя",
        request_body=UserUpdateSerializer,
        responses={200: UserUpdateSerializer(), 400: "Bad request"}
    )
    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя.",
        request_body=UserRegistrationSerializer,
        responses={201: "User registered successfully", 400: "Bad request"}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    # authentication_classes = [CsrfExemptSessionAuthentication]
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Аунтификация пользователя с логином и паролем. Возвращает файл cookie сеанса в случае успеха.",
        request_body=AuthTokenSerializer,
        responses={200: "Login successful", 400: "Invalid credentials"}
    )
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Сохраняем информацию о пользователе в сессии
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Логаут
class UserLogoutView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Выход аунтифицированного пользователя. Удаление сессии.",
        responses={204: "Logout successful"}
    )
    def post(self, request):
        logout(request)  # Удаляем сессию
        return Response({'message': 'Logout successful'}, status=status.HTTP_204_NO_CONTENT)


class ListAnimals(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get a list of requests. Optionally filter by date and status.",
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Filter requests after a specific date",
                              type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter requests by status",
                              type=openapi.TYPE_STRING)
        ],
        responses={200: AnimalSerializer(many=True)}
    )
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                if 'date' in request.data and 'status' in request.data:
                    animals = Animal.objects.filter(formed_at__gte=request.data['date'], status=request.data['status']).exclude(
                        formed_at=None)
                else:
                    animals = Animal.objects.all().exclude(
                        formed_at=None)
            else:
                if 'date' in request.data and 'status' in request.data:
                    animals = Animal.objects.filter(user=request.user, formed_at__gte=request.data['date'], status=request.data['status']).exclude(
                        formed_at=None)
                else:
                    animals = Animal.objects.filter(user=request.user).exclude(
                        formed_at=None)

            animals_serializer = AnimalSerializer(animals, many=True)
            return Response(animals_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Вы не вошли в аккаунт'} ,status=status.HTTP_403_FORBIDDEN)


class GetAnimal(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get details of a request by ID, including associated threats.",
        responses={200: AnimalSerializer()}
    )
    def get(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)
        serializer = AnimalSerializer(animal)
        response = serializer.data

        current_habitats = Habitat.objects.filter(
            habitat_habitat__animal=pk  # Проверка на соответствие стоянки
        ).annotate(
            population=F('habitat_habitat__population')  # Добавляем информацию о капитане из модели ParkingShip
        ).order_by('id')

        habitats_serializer = HabitatListInAnimalSerializer(current_habitats, many=True)
        response['habitats'] = habitats_serializer.data

        return Response(response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a request by ID.",
        request_body=PutAnimalSerializer,
        responses={200: "Request updated successfully", 400: "Bad request"}
    )
    def put(self, request, pk):
        serializer = PutAnimalSerializer(data=request.data)
        if serializer.is_valid():
            animal = get_object_or_404(Animal, pk=pk)
            # animal.type = serializer.validated_data['type']
            # animal.genus = serializer.validated_data['genus']
            for attr, value in serializer.validated_data.items():
                setattr(animal, attr, value)
            animal.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FormAnimal(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Mark a request as formed. Only available for requests with a 'draft' status.",
        responses={200: "Request successfully formed", 400: "Bad request"}
    )
    def put(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)
        if not animal.status == 'draft':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not request.user == animal.user:
           return Response(status=status.HTTP_403_FORBIDDEN)

        # if animal.created_at > datetime.now():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        if not animal.ended_at == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        animal.formed_at = datetime.now()
        animal.status = 'formed'
        animal.save()
        return Response(status=status.HTTP_200_OK)


class ModerateAnimal(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Approve or decline a request (for moderators).",
        request_body=AcceptAnimalSerializer,
        responses={200: "Request moderated successfully", 400: "Bad request"}
    )
    def put(self, request, pk):

        # if not request.user.is_staff:
        #    return Response({'error': 'Вы не можете модерировать заявку'}, status=status.HTTP_403_FORBIDDEN)

        animal = get_object_or_404(Animal, pk=pk)
        serializer = AcceptAnimalSerializer(data=request.data)
        if not animal.status == 'formed':
            return Response({'error': 'Заявка не сформирована'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            if serializer.validated_data['accept'] == True and animal.status:
                animal.status = 'completed'
                animal.moderator = request.user

                # calc final population
                animal_habitats = HabitatAnimal.objects.filter(animal=animal)

                final_population = 0

                for animal_habitat in animal_habitats:
                    final_population += animal_habitat.population

                animal.final_population = final_population
                animal.ended_at = datetime.now()
            else:
                animal.status = 'cancelled'
                animal.moderator = request.user
                animal.ended_at = datetime.now()
            animal.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a request (for moderators).",
        responses={200: "Request deleted successfully"}
    )
    def delete(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)

        # TODO auth
        # if not request.user.is_staff or not request.user == Request:
        #    return Response(status=status.HTTP_403_FORBIDDEN)

        animal.status = 'deleted'
        animal.ended_at = datetime.now()
        animal.save()
        return Response(status=status.HTTP_200_OK)


class EditAnimalHabitat(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Remove a threat from a request.",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={'threat_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the threat")},
        #     required=['threat_id']
        # ),
        responses={200: "Threat removed successfully", 400: "Bad request"}
    )
    def delete(self, request, animal_pk, habitat_pk):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        # if 'habitat_id' in request.data:
        #     record_m_to_m = get_object_or_404(HabitatAnimal, animal=pk, habitat=request.data['habitat_id'])
        #     record_m_to_m.delete()
        #     return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        record_m_to_m = get_object_or_404(HabitatAnimal, animal=animal_pk, habitat=habitat_pk)
        record_m_to_m.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update the price of a threat in a request.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'population': openapi.Schema(type=openapi.TYPE_NUMBER, description="Популяция для МО")
            },
            required=['population']
        ),
        responses={200: "Price updated successfully", 400: "Bad request"}
    )
    def put(self, request, animal_pk, habitat_pk):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if 'population' in request.data:
            record_m_to_m = get_object_or_404(HabitatAnimal, animal=animal_pk, habitat=habitat_pk)
            record_m_to_m.population = request.data['population']
            record_m_to_m.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
