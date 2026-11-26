# Практическая работа 3.2

## Django REST Framework

Проект: `warriors_project`, приложение: `warriors_app`. Все адреса начинаются с `/war/`.

---

## 1. Установка и запуск

```bash
cd warriors_project
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

В `settings.py` в `INSTALLED_APPS` добавлены `rest_framework` и `warriors_app`,
в `urls.py` проекта — `path('war/', include('warriors_app.urls'))`.

## 2. Модель данных

Модели взяты из задания: `Warrior`, `Profession`, `Skill` и ассоциативная сущность
`SkillOfWarrior` (M:N воин — умение с уровнем освоения).

| Модель | Поля | Связи |
|--------|------|-------|
| `Warrior` | `race` (choices), `name`, `level` | FK `profession`, M:N `skill` through `SkillOfWarrior` (`related_name='warrior_skils'`) |
| `Profession` | `title`, `description` | — |
| `Skill` | `title` | — |
| `SkillOfWarrior` | `level` | FK `skill`, FK `warrior` (`related_name='warrior_skill'`) |

## 3. Представления на основе APIView

```python
class WarriorAPIView(APIView):
    def get(self, request):
        warriors = Warrior.objects.all()
        serializer = WarriorSerializer(warriors, many=True)
        return Response({"Warriors": serializer.data})


class ProfessionCreateView(APIView):
    def post(self, request):
        profession = request.data.get("profession")
        serializer = ProfessionCreateSerializer(data=profession)
        if serializer.is_valid(raise_exception=True):
            profession_saved = serializer.save()
        return Response({"Success": "Profession '{}' created succesfully.".format(profession_saved.title)})
```

В примере из задания `ProfessionCreateSerializer.create()` возвращал новый несохранённый
объект `Profession(**validated_data)`; исправлено — возвращается сохранённый объект.
Также в маршруте `path('/warriors/', ...)` убран лишний ведущий `/`.

## 4. Практическое задание «Эндпоинты для скилов»

Реализовано тем же методом (`APIView`):

```python
class SkillCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)


class SkillAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response({"Skills": serializer.data})


class SkillCreateView(APIView):
    def post(self, request):
        skill = request.data.get("skill")
        serializer = SkillCreateSerializer(data=skill)
        if serializer.is_valid(raise_exception=True):
            skill_saved = serializer.save()
        return Response({"Success": "Skill '{}' created succesfully.".format(skill_saved.title)})
```

```http
POST /war/skill/create/
{"skill": {"title": "Python"}}
```

```json
{"Success": "Skill 'Python' created succesfully."}
```

```http
GET /war/skills/
```

```json
{"Skills": [{"id": 1, "title": "Python"}, {"id": 2, "title": "Django"}, {"id": 3, "title": "React"}]}
```

## 5. Generic-классы

```python
class WarriorListAPIView(generics.ListAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class ProfessionCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfessionCreateSerializer
    queryset = Profession.objects.all()
```

Вспомогательные endpoint-ы для заполнения данных: `POST /war/warriors/create/`
(создать воина) и `POST /war/skill_of_warrior/create/` (привязать умение с уровнем).

## 6. Практическое задание «CRUD-эндпоинты для воинов»

Вложенные сериализаторы:

```python
class WarriorWithProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    race = serializers.CharField(source='get_race_display', read_only=True)

    class Meta:
        model = Warrior
        fields = ['id', 'name', 'race', 'level', 'profession']


class SkillWithLevelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='skill.id')
    title = serializers.CharField(source='skill.title')

    class Meta:
        model = SkillOfWarrior
        fields = ['id', 'title', 'level']


class WarriorNestedSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skills = SkillWithLevelSerializer(source='warrior_skill', many=True, read_only=True)
    race = serializers.CharField(source='get_race_display', read_only=True)

    class Meta:
        model = Warrior
        fields = ['id', 'name', 'race', 'level', 'profession', 'skills']
```

Умения выводятся через ассоциативную сущность (`related_name='warrior_skill'`), поэтому
вместе с названием умения виден уровень его освоения.

| № | Задание | Метод и URL | Класс |
|---|---------|-------------|-------|
| 1 | Все воины и их профессии | GET `/war/warriors/professions/` | `ListAPIView` |
| 2 | Все воины и их скилы | GET `/war/warriors/skills/` | `ListAPIView` |
| 3 | Воин по id, его профессия и скилы | GET `/war/warriors/<id>/` | `RetrieveAPIView` |
| 4 | Удаление воина по id | DELETE `/war/warriors/<id>/delete/` | `DestroyAPIView` |
| 5 | Редактирование воина | PUT / PATCH `/war/warriors/<id>/update/` | `UpdateAPIView` |

### 1. Воины и профессии

```json
[{"id": 1, "name": "Дмитрий Мартынов", "race": "developer", "level": 66,
  "profession": {"id": 1, "title": "Backend", "description": "Пишет серверную часть"}},
 {"id": 2, "name": "Никита Михайловский", "race": "student", "level": 15,
  "profession": {"id": 2, "title": "Frontend", "description": "Вёрстка и JS"}}]
```

### 2. Воины и скилы

```json
[{"id": 1, "name": "Дмитрий Мартынов", "race": "developer", "level": 66,
  "skills": [{"id": 1, "title": "Python", "level": 20}, {"id": 2, "title": "Django", "level": 15}]},
 {"id": 2, "name": "Никита Михайловский", "race": "student", "level": 15,
  "skills": [{"id": 3, "title": "React", "level": 12}]}]
```

### 3. Воин по id

```json
{"id": 1, "name": "Дмитрий Мартынов", "race": "developer", "level": 66,
 "profession": {"id": 1, "title": "Backend", "description": "Пишет серверную часть"},
 "skills": [{"id": 1, "title": "Python", "level": 20}, {"id": 2, "title": "Django", "level": 15}]}
```

### 4. Удаление

`DELETE /war/warriors/2/delete/` → `204 No Content`; повторный `GET /war/warriors/2/` →
`404 {"detail": "No Warrior matches the given query."}`.

### 5. Редактирование

```http
PATCH /war/warriors/2/update/
{"level": 25, "race": "t"}
```

```json
{"id": 2, "name": "Никита Михайловский", "race": "t", "level": 25, "profession": 2}
```

## 7. Все маршруты

| Метод | URL | Назначение |
|-------|-----|------------|
| GET | `/war/warriors/` | воины (APIView) |
| POST | `/war/profession/create/` | создать профессию (APIView) |
| GET | `/war/skills/` | скилы (APIView) |
| POST | `/war/skill/create/` | создать скил (APIView) |
| GET | `/war/warriors/list/` | воины (generic) |
| POST | `/war/profession/generic_create/` | создать профессию (generic) |
| POST | `/war/warriors/create/` | создать воина |
| POST | `/war/skill_of_warrior/create/` | привязать скил к воину |
| GET | `/war/skills/related/` | скилы с воинами (обратная сторона M:N) |
| GET | `/war/warriors/related/` | воины со скилами через `SlugRelatedField` |
| GET | `/war/warriors/professions/` | задание 1 |
| GET | `/war/warriors/skills/` | задание 2 |
| GET | `/war/warriors/<id>/` | задание 3 |
| DELETE | `/war/warriors/<id>/delete/` | задание 4 |
| PUT, PATCH | `/war/warriors/<id>/update/` | задание 5 |
