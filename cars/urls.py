from django.urls import path
from . import views

app_name = "cars"

urlpatterns = [
    path("", views.cars_list, name="cars_list"),
    path("new/", views.car_create, name="car_create"),
    path("<int:car_id>/", views.car_detail, name="car_detail"),
    path("<int:car_id>/edit/", views.car_edit, name="car_edit"),
    path("<int:car_id>/delete/", views.car_delete, name="car_delete"),
    path("<int:car_id>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.my_favorites, name="my_favorites"),
    path("history/", views.viewed_history, name="viewed_history"),
]