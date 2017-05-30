from django.contrib import admin

from .models import Person

class FestivusAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date')
    list_filter = ('gender', 'marital_status')

admin.site.register(Person, FestivusAdmin)
