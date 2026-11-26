from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profession, Skill, SkillOfWarrior, Warrior
from .serializers import (ProfessionCreateSerializer, ProfessionSerializer,
                          SkillCreateSerializer, SkillOfWarriorSerializer,
                          SkillRelatedSerializer, SkillSerializer,
                          WarriorNestedSerializer, WarriorRelatedSerializer,
                          WarriorSerializer, WarriorUpdateSerializer,
                          WarriorWithProfessionSerializer, WarriorWithSkillsSerializer)


# ============ Раздел 3: представления на основе APIView ============

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


# ---- Практическое задание «Эндпоинты для скилов» (тем же методом, APIView) ----

class SkillAPIView(APIView):
    """Просмотр всех скилов."""

    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response({"Skills": serializer.data})


class SkillCreateView(APIView):
    """Добавление скила. Тело: {"skill": {"title": "..."}}"""

    def post(self, request):
        skill = request.data.get("skill")
        serializer = SkillCreateSerializer(data=skill)

        if serializer.is_valid(raise_exception=True):
            skill_saved = serializer.save()

        return Response({"Success": "Skill '{}' created succesfully.".format(skill_saved.title)})


# ============ Раздел 5: generic-классы ============

class WarriorListAPIView(generics.ListAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class ProfessionCreateAPIView(generics.CreateAPIView):
    serializer_class = ProfessionCreateSerializer
    queryset = Profession.objects.all()


class WarriorCreateAPIView(generics.CreateAPIView):
    """Создание воина (вспомогательный эндпоинт для заполнения данных)."""
    serializer_class = WarriorUpdateSerializer
    queryset = Warrior.objects.all()


class SkillOfWarriorCreateAPIView(generics.CreateAPIView):
    """Привязать умение к воину с уровнем: {"warrior": 1, "skill": 2, "level": 10}"""
    serializer_class = SkillOfWarriorSerializer
    queryset = SkillOfWarrior.objects.all()


class SkillRelatedListAPIView(generics.ListAPIView):
    """Пример из практики: умения с воинами (обратная сторона M:N)."""
    serializer_class = SkillRelatedSerializer
    queryset = Skill.objects.prefetch_related('warrior_skils')


class WarriorRelatedListAPIView(generics.ListAPIView):
    """Пример из практики: SlugRelatedField."""
    serializer_class = WarriorRelatedSerializer
    queryset = Warrior.objects.prefetch_related('skill')


# ---- Практическое задание «CRUD-эндпоинты для воинов» ----

class WarriorProfessionListAPIView(generics.ListAPIView):
    """1. Полная информация о всех воинах и их профессиях (в одном запросе)."""
    serializer_class = WarriorWithProfessionSerializer
    queryset = Warrior.objects.select_related('profession')


class WarriorSkillListAPIView(generics.ListAPIView):
    """2. Полная информация о всех воинах и их скилах (в одном запросе)."""
    serializer_class = WarriorWithSkillsSerializer
    queryset = Warrior.objects.prefetch_related('warrior_skill__skill')


class WarriorDetailAPIView(generics.RetrieveAPIView):
    """3. Полная информация о воине (по id), его профессии и скилах."""
    serializer_class = WarriorNestedSerializer
    queryset = Warrior.objects.select_related('profession').prefetch_related('warrior_skill__skill')


class WarriorDestroyAPIView(generics.DestroyAPIView):
    """4. Удаление воина по id."""
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class WarriorUpdateAPIView(generics.UpdateAPIView):
    """5. Редактирование информации о воине (PUT / PATCH)."""
    serializer_class = WarriorUpdateSerializer
    queryset = Warrior.objects.all()
