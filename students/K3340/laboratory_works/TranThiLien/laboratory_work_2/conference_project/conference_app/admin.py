from django.contrib import admin
from .models import Conference, Topic, Venue, ConferenceTopic, Registration, Review


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'start_date', 'end_date')
    list_filter = ('start_date', 'venue')
    search_fields = ('title', 'description')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('report_title', 'conference', 'author', 'status', 'recommended')
    list_filter = ('status', 'recommended', 'conference')
    actions = ['mark_recommended', 'mark_not_recommended']

    @admin.action(description='✅ Предлагаемое объявление')
    def mark_recommended(self, request, queryset):
        queryset.update(recommended=True, status='approved')

    @admin.action(description='❌ Не рекомендуется')
    def mark_not_recommended(self, request, queryset):
        queryset.update(recommended=False, status='rejected')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('conference', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'conference')


admin.site.register(Topic)
admin.site.register(Venue)
admin.site.register(ConferenceTopic)