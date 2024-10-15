from django.shortcuts import render
from django.shortcuts import redirect
from django.db import connection
from .models import Habitat, Animal, HabitatAnimal
from django.contrib.auth.models import User

def home(request):
    if not Animal.objects.filter(status='draft').exists():
        habitat_count = 0
        current_request = 0
    else:
        animals = Animal.objects.filter(status='draft')
        current_request = animals.first()
        habitat_count = current_request.animal_habitats.count()

    habitat_name = request.GET.get('habitat_name', '')
    if habitat_name:
        habitats = Habitat.objects.filter(title__icontains=habitat_name)
    else:
        habitats = Habitat.objects.all()

    return render(request, 'main/index.html', {'data' : {
        'habitats': habitats,
        'count_hab': habitat_count,
        'animal_id': current_request.id if current_request else 0
    }})

def habitat(request, id):
    current_habitat = Habitat.objects.get(id=id)
    return render(request, 'main/habitat.html', {'current_habitat': current_habitat})

def animal(request, id):
    if id == 0:
        return render(request, 'main/animal.html', {'current_request': None})

    if Animal.objects.filter(id=id).exclude(status='draft').exists():
        return render(request, 'main/animal.html', {'current_request': None})

    if not Animal.objects.filter(id=id).exists():
        return render(request, 'main/animal.html', {'current_request': None})

    req_id = id
    current_request = Animal.objects.get(id=id)
    habitat_ids = HabitatAnimal.objects.filter(animal=current_request).values_list('habitat_id', flat=True)
    current_habitats = Habitat.objects.filter(id__in=habitat_ids)

    return render(request, 'main/animal.html', {'data' : {
        'current_habitats': current_habitats,
        'current_request': current_request,
        'req_id':req_id
    }})

def add_habitat(request):
    if request.method == 'POST':
        if not Animal.objects.filter(status='draft').exists():
            animal = Animal()
            animal.user_id = request.user.id
            animal.save()
        else:
            animal = Animal.objects.get(status='draft')

        habitat_id = request.POST.get('habitat_id')
        new_habitat = Habitat.objects.get(id=habitat_id)
        if HabitatAnimal.objects.filter(animal=animal, habitat=new_habitat).exists():
            return redirect('/')
        animal_habitat = HabitatAnimal(animal=animal, habitat=new_habitat)
        animal_habitat.save()
        return redirect('/')
    else:
        return redirect('/')


def del_animal(request):
    if request.method == 'POST':
        animal_id = request.POST.get('animal_id')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE animals SET status = %s WHERE id = %s", ['deleted', animal_id])
        return redirect('/')
    else:
        return redirect('/')