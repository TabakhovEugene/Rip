from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import *
from .models import Animal, Habitat, HabitatAnimal
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from datetime import datetime


class HabitatList(APIView):
    model_class = Habitat
    serializer_class = HabitatListSerializer

    # def get(self, request, format=None):
    #     habitats = self.model_class.objects.all()
    #     serializer = self.serializer_class(habitats, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    # получить список мест обитаний
    def get(self, request):
        if 'title' in request.GET:
            habitats = self.model_class.objects.filter(title__icontains=request.GET['title'])
        else:
            habitats = self.model_class.objects.all()

        serializer = self.serializer_class(habitats, many=True)
        resp = serializer.data
        draft_request = Animal.objects.filter(user=request.user, status='draft').first()
        if draft_request:
            request_serializer = AnimalSerializer(draft_request)  # Use RequestSerializer here
            resp.append({'request': request_serializer.data})

        return Response(resp, status=status.HTTP_200_OK)


class HabitatDetail(APIView):
    model_class = Habitat
    serializer_class = HabitatDetailSerializer

    # получить место обитания
    def get(self, request, pk):
        habitat = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(habitat)
        return Response(serializer.data)

    # удалить место обитания (для модератора)
    def delete(self, request, pk):

        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        habitat = get_object_or_404(self.model_class, pk=pk)
        habitat.status = 'deleted'
        habitat.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # добавить новое место обитания (для модератора)
    def post(self, request, format=None):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # обновление места обитания (для модератора)
    def put(self, request, pk, format=None):

        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)

        habitat = get_object_or_404(self.model_class, id=pk)
        serializer = self.serializer_class(habitat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddHabitatView(APIView):
    # добавление услуги в заявку
    def post(self, request):
        # создаем заявку, если ее еще нет
        if not Animal.objects.filter(user=request.user, status='draft').exists():
            new_animal = Animal()
            new_animal.user = request.user
            new_animal.save()
        # else:
        #     new_animal = Animal.objects.filter(user=request.user, status='draft')

        animal_id = Animal.objects.filter(user=request.user, status='draft').first().id
        serializer = AnimalHabitatSerializer(data=request.data)
        if serializer.is_valid():
            new_animal_habitat = HabitatAnimal()
            new_animal_habitat.habitat_id = serializer.validated_data["habitat_id"]
            new_animal_habitat.animal_id = animal_id
            if 'population' in request.data:
                new_animal_habitat.population = request.data["population"]
            new_animal_habitat.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    def post(self, request):
        # if not request.user.is_staff:
        #    return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AddImageSerializer(data=request.data)
        if serializer.is_valid():
            habitat = Habitat.objects.get(pk=serializer.validated_data['habitat_id'])
            habitat.picture_url = serializer.validated_data['picture_url']
            habitat.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# USER VIEWS
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Личный кабинет (обновление профиля)
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Аутентификация пользователя
class UserLoginView(APIView):
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Деавторизация пользователя
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # Удаляем токен
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListAnimals(APIView):
    def get(self, request):
        if 'date' in request.data and 'status' in request.data:
            animals = Animal.objects.filter(formed_at__gte=request.data['date'], status=request.data['status']).exclude(
                formed_at=None)
        else:
            animals = Animal.objects.all()
        # animals = Animal.objects.filter(status=request.data['status'])
        animals_serializer = AnimalSerializer(animals, many=True)
        return Response(animals_serializer.data, status=status.HTTP_200_OK)


class GetAnimal(APIView):
    def get(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)
        serializer = AnimalSerializer(animal)

        animal_habitats = HabitatAnimal.objects.filter(animal=animal)
        habitats_ids = []
        for animal_habitat in animal_habitats:
            habitats_ids.append(animal_habitat.habitat_id)

        habitats_in_animal = []
        for id in habitats_ids:
            habitats_in_animal.append(get_object_or_404(Habitat, pk=id))

        habitats_serializer = HabitatListSerializer(habitats_in_animal, many=True)
        response = serializer.data
        response['habitats'] = habitats_serializer.data

        return Response(response, status=status.HTTP_200_OK)

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
    def put(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)
        if not animal.status == 'draft':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # if not request.user == req.user:
        #    return Response(status=status.HTTP_403_FORBIDDEN)

        # if animal.created_at > datetime.now():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        if not animal.ended_at == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        animal.formed_at = datetime.now()
        animal.status = 'formed'
        animal.save()
        return Response(status=status.HTTP_200_OK)


class ModerateAnimal(APIView):
    def put(self, request, pk):

        # if not request.user.is_staff:
        #    return Response(status=status.HTTP_403_FORBIDDEN)

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
            else:
                animal.status = 'cancelled'
                animal.moderator = request.user
                animal.ended_at = datetime.now()
            animal.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    def delete(self, request, pk):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        if 'habitat_id' in request.data:
            record_m_to_m = get_object_or_404(HabitatAnimal, animal=pk, habitat=request.data['habitat_id'])
            record_m_to_m.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # if not request.user.is_staff:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        if 'habitat_id' in request.data and 'population' in request.data:
            record_m_to_m = get_object_or_404(HabitatAnimal, animal=pk, habitat=request.data['habitat_id'])
            record_m_to_m.population = request.data['population']
            record_m_to_m.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
