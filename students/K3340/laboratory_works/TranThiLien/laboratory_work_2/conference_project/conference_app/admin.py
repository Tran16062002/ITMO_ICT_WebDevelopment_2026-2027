from django.contrib import admin
from .models import Conference, Topic, Venue

admin.site.register(Conference)
admin.site.register(Topic)
admin.site.register(Venue)