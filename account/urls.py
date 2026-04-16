from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("register/verify/",views.verify_email_view, name="verify_email"),
    path("perfil/", views.profile_view, name="profile"),
]