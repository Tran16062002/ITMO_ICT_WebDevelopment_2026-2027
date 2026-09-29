from django.urls import path
from . import views

urlpatterns = [
    path('conference/<int:conference_id>/', views.conference_detail, name='conference_detail'),
]