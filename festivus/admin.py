from django.contrib import admin

from .models import Person, Team, Membership, Payment, PlaceClassification, Place, EventType, Event, Transaction

#most probably we should have reporting for a specific event including total cost
#maybe later on stats on expenses and most expesive events

class MonthFilter(admin.SimpleListFilter):
    title = 'Month'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        monthes = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        month_filter = []
        for i in range(len(monthes)):
            month_filter.append((i+1, monthes[i]))
        return month_filter
    
    def queryset(self, request, queryset):
        excludes = []
        if self.value():
            for person in queryset.all():
                if person.birth_date.month != int(self.value()):
                    excludes.append(person.id)
            return queryset.exclude(id__in=excludes)
        return queryset


class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'email', 'squad_member', 'active')
    list_filter = (MonthFilter, 'team', 'gender', 'marital_status', 'squad_member', 'active')
    search_fields = ('first_name', 'last_name', 'team__name')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'month', 'amount', 'currency')
    list_filter = ('year', 'month', 'currency', 'collected_by__first_name')
    search_fields = ('person__first_name', 'amount', 'notes')
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj: # disable editing the amount of an existing payment since it links to transactions
            return self.readonly_fields + ('amount', 'currency')
        return self.readonly_fields

    # define the raw_id_fields
    raw_id_fields = ('person',)
    # define the autocomplete_lookup_fields
    autocomplete_lookup_fields = {
        'fk': ['person'],
        #'m2m': ['collected_by'],
    }

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('event', 'amount', 'currency', 'payment_date', 'notes')
    list_filter = ('event__event_type__name', 'payment_date', 'notes')
    search_fields = ('event__name', 'amount', 'notes')
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj: # disable editing the amount of an existing payment since it links to transactions
            return self.readonly_fields + ('amount', 'currency')
        return self.readonly_fields

    # define the raw_id_fields
    raw_id_fields = ('event',)
    # define the autocomplete_lookup_fields
    autocomplete_lookup_fields = {
        'fk': ['event'],
        #'m2m': ['collected_by'],
    }

class PlaceClassificationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('classification', 'name', 'rating')
    list_filter = ('classification', 'rating')
    search_fields = ('name', 'description', 'comment')

class EventTypeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'organizer', 'event_date', 'gift_card', 'total')
    list_filter = ('event_type__name', 'event_date', 'order_from__name')
    search_fields = ('event_date', 'notes', 'location')
    
    # define the raw_id_fields
    raw_id_fields = ('targets',)
    # define the autocomplete_lookup_fields
    autocomplete_lookup_fields = {
        'm2m': ['targets'],
        #'m2m': ['collected_by'],
    }

class TransactionAdmin(admin.ModelAdmin):
    #Add event_total To list_display and assert it's equal to total
    list_display = ('event', 'transaction_date', 'transaction_type', 'amount', 'currency', 'dollar_total', 'note')
    list_filter = ('transaction_type', 'currency', 'transaction_date', 'description')
    search_fields = ('event__targets__first_name', 'event__targets__last_name', 'note', 'event__name')
    readonly_fields = ('total',)

    def event_total(self, obj):
        return obj.event_total

admin.site.register(Person, PersonAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PlaceClassification, PlaceClassificationAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Membership, MembershipAdmin)

