from django import forms
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