from django.urls import path
from . import views

app_name = "cars"

urlpatterns = [
    path("", views.cars_list, name="cars_list"),
    path("compare/", views.compare_cars, name="compare_cars"),
    path("new/", views.car_create, name="car_create"),
    path("mapa/", views.map_view, name="map"),

    path("favorites/", views.my_favorites, name="my_favorites"),
    path("history/", views.viewed_history, name="viewed_history"),

    path("lists/", views.car_lists, name="car_lists"),
    path("lists/create/", views.car_list_create, name="car_list_create"),
    path("lists/<int:list_id>/", views.car_list_detail, name="car_list_detail"),
    path("lists/<int:list_id>/delete/", views.car_list_delete, name="car_list_delete"),
    path("lists/<int:list_id>/remove/<int:car_id>/", views.remove_car_from_list, name="remove_car_from_list"),

    path("<int:car_id>/", views.car_detail, name="car_detail"),
    path("<int:car_id>/edit/", views.car_edit, name="car_edit"),
    path("<int:car_id>/delete/", views.car_delete, name="car_delete"),
    path("<int:car_id>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("<int:car_id>/lists/add/", views.add_car_to_lists, name="add_car_to_lists"),
    path("<int:car_id>/toggle-sold/", views.toggle_sold, name="toggle_sold"),
]