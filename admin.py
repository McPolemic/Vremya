from vremya.models import Activity,Event
from django.contrib import admin

class EventAdmin(admin.ModelAdmin):
    list_display = ('date', 'activity', 'english_time', 'frac_hours')
    list_filter = ['date', 'activity']
    date_hierarchy = 'date'

admin.site.register(Activity)
admin.site.register(Event, EventAdmin)
