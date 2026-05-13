from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'car', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('reporter__username', 'car__make', 'car__model', 'description')
    list_editable = ('status',)
    ordering = ('-created_at',)
