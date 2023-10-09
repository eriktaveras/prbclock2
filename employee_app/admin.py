from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Employee, TimeRecord

class TimeRecordInline(admin.TabularInline):
    model = TimeRecord
    extra = 0
    readonly_fields = ['date', 'time_in', 'time_out', 'lunch_time']

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')  # Removed 'id' for better readability
    search_fields = ('name', 'position')
    list_filter = ('position',)
    inlines = [TimeRecordInline]
    ordering = ['name']  # Default ordering

    fieldsets = (
        (_('Personal Information'), {'fields': ('name', 'position')}),
    )

class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out', 'lunch_time')  # Removed 'id' for better readability
    search_fields = ('employee__name', 'date')
    list_filter = ('date', 'employee')
    date_hierarchy = 'date'  # Makes it easier to navigate through dates
    ordering = ['date', 'employee']  # Default ordering

    fieldsets = (
        (_('Time Record Information'), {'fields': ('employee', 'date', 'time_in', 'time_out', 'lunch_time')}),
    )

    list_select_related = ('employee',)  # Optimize SQL queries

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(TimeRecord, TimeRecordAdmin)
