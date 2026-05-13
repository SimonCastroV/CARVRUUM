from django.urls import path
from . import views

urlpatterns = [
    path('<int:car_id>/report/', views.report_car, name='report_car'),
]
