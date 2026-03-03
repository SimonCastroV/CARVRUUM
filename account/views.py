from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
from .models import Profile

from cars.models import Car, Favorite


def landing(request):
    total_cars = Car.objects.filter(is_active=True).count()

    my_cars_count = 0
    my_favorites_count = 0
    if request.user.is_authenticated:
        my_cars_count = Car.objects.filter(owner=request.user).count()
        my_favorites_count = Favorite.objects.filter(user=request.user).count()

    return render(request, "account/landing.html", {
        "total_cars": total_cars,
        "my_cars_count": my_cars_count,
        "my_favorites_count": my_favorites_count,
    })


def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.user.is_authenticated:
        return redirect(next_url or "home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url or "home")
    else:
        form = AuthenticationForm()

    return render(request, "account/login.html", {"form": form, "next": next_url})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.telefono = form.cleaned_data.get("telefono")
            profile.ciudad = form.cleaned_data.get("ciudad_residencia")
            profile.save()

            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "account/register.html", {"form": form})


@login_required
def home(request):
    profile = getattr(request.user, "profile", None)

    my_cars_count = Car.objects.filter(owner=request.user).count()
    my_favorites_count = Favorite.objects.filter(user=request.user).count()

    return render(request, "account/home.html", {
        "username": request.user.username,
        "ciudad": profile.ciudad if profile else None,
        "my_cars_count": my_cars_count,
        "my_favorites_count": my_favorites_count,
    })