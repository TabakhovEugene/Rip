from django.shortcuts import render

HABITATS = [
            {'title': 'Африка', 'pic': 'http://127.0.0.1:9000/test/Африка.jpg', 'id': 1,
             'desc_pic': 'http://127.0.0.1:9000/test/африкаа.png',
             'desc': 'Климат Африки, расположенной в зоне повышенной освещённости и обласканной щедрыми лучами солнца, весьма благоприятствует обитанию на его территории самых разнообразных форм жизни. Именно поэтому фауна континента чрезвычайно богата, а про животных Африки ходит множество замечательных легенд и удивительных историй. Для сохранения фауны в Африке были созданы крупнейшие национальные и природные парки, заповедники и заказники. Их численность на планете самая большая именно здесь. В зависимости от погодно-климатических условий на материке сформировались различные природные зоны: пустыни и полупустыни, саванны, джунгли, экваториальные леса. В разных уголках континента проживают хищники и крупные копытные животные, грызуны и птицы, змеи и ящерицы, насекомые, а в реках водятся крокодилы и рыбы. Здесь обитает огромное количество разных видов обезьян.'},
            {'title': 'Австралия', 'pic': 'http://127.0.0.1:9000/test/Австралия.jpg', 'id': 2,
             'desc_pic': 'http://127.0.0.1:9000/test/австралия.png',
             'desc': 'Когда речь заходит о животном мире Австралии, сразу вспоминается кенгуру. Это животное действительно является, своего рода, символом данного материка и даже присутствует на государственном гербе. Но, помимо разнообразных кенгуру, в австралийскую фауну входят еще около 200000 живых существ. Поскольку материк отличается сравнительно небольшими размерами и расположен вдалеке от «большой земли», большинство животных, птиц и насекомых являются эндемиками. Здесь широко представлены древесные и прыгающие животные, ящерицы и змеи. Также разнообразен птичий мир.'},
            {'title': 'Арктика', 'pic': 'http://127.0.0.1:9000/test/Арктика.jpg', 'id': 3,
             'desc_pic': 'http://127.0.0.1:9000/test/Арктикаа.png',
             'desc': 'Фауна Антарктики представлена отдельными видами беспозвоночных, птиц, млекопитающих. В настоящее время в Антарктиде обнаружено не менее 70 видов беспозвоночных, гнездятся четыре вида пингвинов. На территории полярной области найдены ископаемые остатки нескольких видов нептичьих динозавров. Свободными от ледников и снега остаётся только 2% территории материковой Антарктики. Большая часть фауны Антарктиды представлена на нескольких «аренах жизни»: прибрежные острова и льды, прибрежные оазисы на материке (например, «оазис Бангера»), арена нунатаков (гора Амундсена возле Мирного, гора Нансена на Земле Виктории и др.) и арена ледникового щита. Животные наиболее распространены в приморской полосе (только здесь встречаются тюлени и пингвины). Есть здесь и свои эндемики, например, чёрный комар-звонец Belgica antarctica.'},
            {'title': 'Антарктида', 'pic': 'http://127.0.0.1:9000/test/Антарктида.jpg', 'id': 4,
             'desc_pic': 'http://127.0.0.1:9000/test/Антарктида.png',
             'desc': 'В Антарктиде наблюдается относительно небольшое видовое разнообразие по сравнению с большей частью остального мира. Жизнь на суше сосредоточена в районах, прилегающих к побережью. Перелетные птицы гнездятся на более теплых берегах полуострова и субантарктических островов. Восемь видов пингвинов населяют Антарктиду и ее прибрежные острова. Они делят эти территории с семью видами ластоногих. Южный океан, окружающий Антарктиду, является домом для 10 китообразных, многие из которых мигрируют. На материке очень мало наземных беспозвоночных, хотя те виды, которые там обитают, имеют высокую плотность популяции. Высокая плотность беспозвоночных также наблюдается в океане, где антарктический криль летом образует плотные и обширные скопления. Донные сообщества животных также существуют по всему континенту.'},
            {'title': 'Евразия', 'pic': 'http://127.0.0.1:9000/test/Евразия.jpg', 'id': 5,
             'desc_pic': 'http://127.0.0.1:9000/test/евразия.png',
             'desc': 'Животный мир самого большого материка Земли уникален и разнообразен. Площадь Евразии составляет 54 млн. м². Обширная территория проходит через все географические пояса нашей планеты, поэтому в этом регионе можно встретить самые непохожие друг на друга виды животных. Одной из крупных составляющих материка является тайга, в которой можно встретить медведей, рысей, белок, росомах и других представителей биологических организмов. В горах обитают бурые медведи, а среди лесной фауны выделяются благородный олень, зубр, лисица, косуля и другие. В естественных водоемах можно найти большое количество разнообразной рыбы, в том числе, щуку, плотву, карпов и сомов.'},
            {'title': 'Северная Америка', 'pic': 'http://127.0.0.1:9000/test/Сев_Америка.jpg', 'id': 6,
             'desc_pic': 'http://127.0.0.1:9000/test/Сев_Америка.png',
             'desc': 'Климат Северной Америки холодный в приполярной части, умеренный в субтропической и теплый в тропической. Широкое разнообразие природных зон послужило основой для развития разнообразных популяций животных. Благодаря этому на территории материка обитают необыкновенные представители фауны, которые с легкостью преодолевают неблагоприятные природные условия, выраженные километровыми ледниками, жаркими и знойными пустынями, участками с повышенной влагой. На севере Америки можно встретить белых медведей, зубров и моржей, на юге – грызунов, косуль и куропаток, в центральной части материка – огромное множество птиц, рыбы, рептилий и млекопитающих.'},
            {'title': 'Южная Америка', 'pic': 'http://127.0.0.1:9000/test/Юж_Америка.jpg', 'id': 7,
             'desc_pic': 'http://127.0.0.1:9000/test/Юж_Америка.PNG',
             'desc': 'Южная Америка является домом для огромного количества животных и растений. На территории материка можно найти и ледники, и пустыни. Разные природно-климатические зоны способствуют размещению сотен тысяч видов флоры и фауны. Из-за разнообразия погодных условий список животных также очень обширный и впечатляет неповторимыми чертами. Так, на территории Южной Америки обитают представители млекопитающих, птиц, рыб, насекомых, амфибий и рептилий. Материк считается одним из самых важных на планете. Здесь расположен горный хребет Анды, препятствующий проникновению западных ветров, усиливающий влажность и способствующий выпадению большого количества осадков.'},
        ]

ANIMALS = [
    {
        'id': 1,
        'type': ['Тигр', 'Волк обыкновенный', 'Медведь бурый', 'Олень северный'],
        'genus': ['Волки', 'Пантеры', 'Медведи', 'Олени'],
        'habs_id': [1, 2],
        'm-m': [
            {
                'id': 1,
                'animal_id': 1,
                'habitat_id': 2,
                'count': 10000
            }
        ]
    }
]

def home(request):
    count_hab = len(ANIMALS[0]['habs_id'])
    animal_id = ANIMALS[0]['id']
    ftitle = request.GET.get('habitat', "")
    hab_filtered = HABITATS
    if ftitle != "":
        hab_filtered = list(filter(lambda x: ftitle.lower() in x['title'].lower(), HABITATS))
    return render(request, 'main/index.html', {'data' : {
        'habitats': hab_filtered,
        'count_hab': count_hab,
        'animal_id': animal_id
    }})

def habitat(request, id):
    hab = list(filter(lambda x: x['id'] == id, HABITATS))[0]
    title = hab['title']
    desc = hab['desc']
    desc_pic = hab['desc_pic']
    return render(request, 'main/habitat.html', {'data' : {
        'title': title,
        'desc': desc,
        'desc_pic': desc_pic,
        'id': id
    }})

def basket(request, id):
    types = ANIMALS[0]['type']
    genuses = ANIMALS[0]['genus']

    return render(request, 'main/basket.html', {'data' : {
        'habitats': HABITATS,
        'animals': ANIMALS,
        'types': types,
        'genuses': genuses,
    }})
