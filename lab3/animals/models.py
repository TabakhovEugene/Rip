from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Habitat(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)

    class Status(models.TextChoices):
        ACTIVE = "active", "действует"
        DELETED = "deleted", "удален"
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)

    picture_url = models.URLField(null=False)
    description_picture_url = models.URLField(null=False)

    class Meta:
        managed = True
        db_table = 'habitats'

class Animal(models.Model):
    type = models.TextField(max_length=100, null=False)
    genus = models.TextField(max_length=100, null=False)

    class Status(models.TextChoices):
        DRAFT = "draft", "черновик"
        FORMED = "formed", "сформирован"
        COMPLETED = "completed", "завершён"
        CANCELLED = "cancelled", "откланен"
        DELETED = "deleted", "удален"

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(null=False, default=datetime.now())
    formed_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moderator = models.ForeignKey(User, null=True, related_name='moderator_id', on_delete=models.CASCADE)
    # user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, blank=False)
    # moderator = models.ForeignKey('AuthUser',null=True,related_name='moderator_id',on_delete=models.CASCADE)
    final_population = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'animals'

class HabitatAnimal(models.Model):
    habitat = models.ForeignKey(Habitat, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='animal_habitats')
    population = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'habitats_animals'
        constraints = [
            models.UniqueConstraint(fields=['habitat', 'animal'], name='unique_habitat_animal')
        ]
