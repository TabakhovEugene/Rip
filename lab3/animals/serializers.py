from .models import Habitat, Animal, HabitatAnimal
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class AddImageSerializer(serializers.Serializer):
    habitat_id = serializers.IntegerField(required=True)
    picture_url = serializers.URLField(required=True)

    def validate(self, data):
        habitat_id = data.get('habitat_id')

        # Дополнительная логика валидации, например проверка на существование этих id в базе данных
        if not Habitat.objects.filter(pk=habitat_id).exists():
            raise serializers.ValidationError(f"habitat_id is incorrect")

        return data


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ["pk", "type", "genus", "status", "created_at", "formed_at", "ended_at", "user", "moderator", "final_population"]


class PutAnimalSerializer(serializers.ModelSerializer):
    type = serializers.CharField()
    genus = serializers.CharField()
    class Meta:
        model = Animal
        fields = ["type", "genus", "status", "created_at", "formed_at", "ended_at", "user", "moderator", "final_population"]


class HabitatDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitat
        fields = ["pk", "title", "description", "status", "picture_url", "description_picture_url"]


class HabitatListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habitat
        fields = ["pk", "title", "description", "status", "picture_url"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitat
        fields = ["pk", "picture_url"]


class AnimalHabitatSerializer(serializers.Serializer):
    habitat_id = serializers.IntegerField(required=True)
    population = serializers.IntegerField(required=False)

    def validate(self, data):
        habitat_id = data.get('habitat_id')

        # Дополнительная логика валидации, например проверка на существование этих id в базе данных
        if not Habitat.objects.filter(id=habitat_id).exists():
            raise serializers.ValidationError(f"habitat_id is incorrect")

        return data


# AUTH SERIALIZERS

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Неверные учетные данные")
        return {'user': user}


class CheckUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Пользователь не существует")

        return data


class AcceptAnimalSerializer(serializers.Serializer):
    accept = serializers.BooleanField()