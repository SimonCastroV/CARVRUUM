from django.contrib import admin
from .models import Car, CarImage, CarList, CarListItem


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 0


class CarListItemInline(admin.TabularInline):
    model = CarListItem
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "make", "model", "year", "price", "city", "owner", "is_active", "created_at")
    list_filter = ("is_active", "city", "year")
    search_fields = ("make", "model", "city", "owner__username")
    inlines = [CarImageInline]


@admin.register(CarList)
class CarListAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description", "user__username")
    inlines = [CarListItemInline]


@admin.register(CarListItem)
class CarListItemAdmin(admin.ModelAdmin):
    list_display = ("id", "car_list", "car", "added_at")
    list_filter = ("added_at",)
    search_fields = ("car_list__name", "car__make", "car__model")


admin.site.register(CarImage)