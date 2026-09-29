from django.shortcuts import render, get_object_or_404
from .models import Conference


def conference_detail(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    return render(request, 'conference_detail.html', {'conference': conference})