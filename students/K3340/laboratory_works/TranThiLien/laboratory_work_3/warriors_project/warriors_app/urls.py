from django.urls import path

from .views import *

app_name = "warriors_app"

urlpatterns = [
    # APIView (раздел 3)
    path('warriors/', WarriorAPIView.as_view()),
    path('profession/create/', ProfessionCreateView.as_view()),

    # Практическое задание: скилы (APIView)
    path('skills/', SkillAPIView.as_view()),
    path('skill/create/', SkillCreateView.as_view()),

    # Generic (раздел 5)
    path('warriors/list/', WarriorListAPIView.as_view()),
    path('profession/generic_create/', ProfessionCreateAPIView.as_view()),
    path('warriors/create/', WarriorCreateAPIView.as_view()),
    path('skill_of_warrior/create/', SkillOfWarriorCreateAPIView.as_view()),
    path('skills/related/', SkillRelatedListAPIView.as_view()),
    path('warriors/related/', WarriorRelatedListAPIView.as_view()),

    # Практическое задание: CRUD-эндпоинты для воинов
    path('warriors/professions/', WarriorProfessionListAPIView.as_view()),
    path('warriors/skills/', WarriorSkillListAPIView.as_view()),
    path('warriors/<int:pk>/', WarriorDetailAPIView.as_view()),
    path('warriors/<int:pk>/delete/', WarriorDestroyAPIView.as_view()),
    path('warriors/<int:pk>/update/', WarriorUpdateAPIView.as_view()),
]
