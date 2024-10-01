from django.contrib import admin
from .models import Habitat
from .models import Animal
from .models import HabitatAnimal

# Register your models here.
admin.site.register(Habitat)
admin.site.register(Animal)

@admin.register(HabitatAnimal)
class HabitatAnimalAdmin(admin.ModelAdmin):
    list_display = ('animal_id', 'habitat_id')
    search_fields = ('animal_id', 'habitat_id')
