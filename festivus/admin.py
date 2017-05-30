from django.contrib import admin

from .models import Person, Payment, PlaceCategory, Place, EventType, Event

class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'email')
    list_filter = ('gender', 'marital_status')
    search_fields = ('first_name', 'last_name')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('person', 'month', 'amount', 'currency', 'enrolled')
    list_filter = ('year', 'month', 'currency', 'enrolled')
    search_fields = ('person__first_name', 'amount')

class PlacesCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', '')

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'rating')
    list_filter = ('category', 'rating')
    search_fields = ('name', 'description', 'comment')

class EventTypeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'victim', 'event_date', 'gift_card')
    list_filter = ('event_type', 'organizer')
    search_fields = ('event_type__name', 'description', 'comment', 'location')

admin.site.register(Person, PersonAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PlaceCategory, PlacesCategoryAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)
