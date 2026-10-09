from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Registration, Review, Conference


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['report_title', 'abstract']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['title', 'topics', 'venue', 'start_date', 'end_date',
                  'description', 'venue_desc', 'conditions']

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    """Form đăng ký user mới — kế thừa UserCreationForm của Django"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password1', 'password2']