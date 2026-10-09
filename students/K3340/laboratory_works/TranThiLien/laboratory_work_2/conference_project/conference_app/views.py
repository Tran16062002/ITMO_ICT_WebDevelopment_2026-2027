from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Conference, Registration, Review
from .forms import RegistrationForm, ReviewForm, ConferenceForm


# ============ FBV ============
def conference_list(request):
    conferences = Conference.objects.all().order_by('-start_date')
    return render(request, 'conference_list.html', {'conferences': conferences})


def conference_detail(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    return render(request, 'conference_detail.html', {
        'conference': conference,
        'reviews': conference.reviews.all(),
        'registrations': conference.registrations.all(),
    })


@login_required
def conference_create(request):
    if request.method == 'POST':
        form = ConferenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo hội nghị')
            return redirect('conference_list')
    else:
        form = ConferenceForm()
    return render(request, 'conference_form.html', {'form': form})


@login_required
def review_create(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.conference = conference
            review.save()
            return redirect('conference_detail', conference_id=conference.id)
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form, 'conference': conference})


# ============ CBV ============
class RegistrationCreateView(CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = 'registration_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.conference_id = self.kwargs['conference_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('conference_detail', kwargs={'conference_id': self.kwargs['conference_id']})


class RegistrationUpdateView(UpdateView):
    model = Registration
    form_class = RegistrationForm
    template_name = 'registration_form.html'

    def get_queryset(self):
        return Registration.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('conference_detail', kwargs={'conference_id': self.object.conference.id})


class RegistrationDeleteView(DeleteView):
    model = Registration
    template_name = 'registration_confirm_delete.html'

    def get_queryset(self):
        return Registration.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('conference_detail', kwargs={'conference_id': self.object.conference.id})