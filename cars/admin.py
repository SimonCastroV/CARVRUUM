from django.contrib import admin
from .models import Car, CarImage


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "make", "model", "year", "price", "city", "owner", "is_active", "created_at")
    list_filter = ("is_active", "city", "year")
    search_fields = ("make", "model", "city", "owner__username")
    inlines = [CarImageInline]


admin.site.register(CarImage)