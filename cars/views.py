from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CarForm
from .models import Car, CarImage, Favorite


def _normalize_phone_to_wa(phone: str) -> str | None:
    if not phone:
        return None
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if not digits:
        return None
    # Colombia: si son 10 dígitos, asumimos +57
    if len(digits) == 10:
        digits = "57" + digits
    return digits


def cars_list(request):
    q = (request.GET.get("q") or "").strip()
    city = (request.GET.get("city") or "").strip()
    max_price_raw = (request.GET.get("max_price") or "").strip()

    cars_qs = (
        Car.objects.filter(is_active=True)
        .select_related("owner", "owner__profile")
        .prefetch_related("images")
    )

    # --- Mejora búsqueda: tokens (ej: "Mazda 2018") ---
    if q:
        tokens = [t for t in q.split() if t]
        for t in tokens:
            cars_qs = cars_qs.filter(
                Q(make__icontains=t) |
                Q(model__icontains=t) |
                Q(year__icontains=t)
            )

    if city:
        cars_qs = cars_qs.filter(city__icontains=city)

    if max_price_raw.isdigit():
        cars_qs = cars_qs.filter(price__lte=int(max_price_raw))

    cars = cars_qs.order_by("-created_at")

    # --- Favoritos ---
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list("car_id", flat=True)
        )

    # --- Sugerencias (desde BD) ---
    base = Car.objects.filter(is_active=True)

    available_makes = (
        base.exclude(make__isnull=True)
        .exclude(make__exact="")
        .values_list("make", flat=True)
        .distinct()
        .order_by("make")
    )

    available_cities = (
        base.exclude(city__isnull=True)
        .exclude(city__exact="")
        .values_list("city", flat=True)
        .distinct()
        .order_by("city")  # alfabético
    )

    return render(request, "cars/cars_list.html", {
        "cars": cars,
        "favorite_ids": favorite_ids,
        "q": q,
        "city": city,
        "max_price": max_price_raw,
        "available_makes": list(available_makes),
        "available_cities": list(available_cities),
    })


def car_detail(request, car_id: int):
    car = get_object_or_404(
        Car.objects.select_related("owner", "owner__profile").prefetch_related("images"),
        id=car_id,
        is_active=True,
    )

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, car=car).exists()

    # WhatsApp del vendedor (si tiene teléfono en Profile)
    seller_phone = getattr(getattr(car.owner, "profile", None), "telefono", "") or ""
    wa_number = _normalize_phone_to_wa(seller_phone)

    car_url = request.build_absolute_uri(f"/cars/{car.id}/")
    msg = f"Hola! Me interesa tu {car.make} {car.model} {car.year}. ¿Sigue disponible? {car_url}"
    seller_whatsapp_url = f"https://wa.me/{wa_number}?text={quote(msg)}" if wa_number else None

    return render(request, "cars/car_detail.html", {
        "car": car,
        "is_favorite": is_favorite,
        "seller_whatsapp_url": seller_whatsapp_url,
        "seller_phone": seller_phone,
    })


@login_required
def toggle_favorite(request, car_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    car = get_object_or_404(Car, id=car_id, is_active=True)

    fav, created = Favorite.objects.get_or_create(user=request.user, car=car)
    if not created:
        fav.delete()

    back = request.META.get("HTTP_REFERER")
    return redirect(back or "cars:cars_list")


@login_required
def car_create(request):
    images_error = None

    if request.method == "POST":
        car_form = CarForm(request.POST)
        files = request.FILES.getlist("images")

        if not files:
            images_error = "Debes subir al menos 1 foto."
        elif len(files) > 10:
            images_error = "Máximo 10 fotos por publicación."
        else:
            for f in files:
                ct = (getattr(f, "content_type", "") or "")
                if not ct.startswith("image/"):
                    images_error = "Solo se permiten archivos de imagen."
                    break

        if car_form.is_valid() and images_error is None:
            with transaction.atomic():
                car = car_form.save(commit=False)
                car.owner = request.user
                car.save()

                for f in files:
                    CarImage.objects.create(car=car, image=f)

            return redirect("cars:cars_list")

    else:
        car_form = CarForm()

    return render(request, "cars/car_create.html", {
        "car_form": car_form,
        "images_error": images_error,
    })

@login_required
def car_edit(request, car_id: int):
    car = get_object_or_404(Car, id=car_id, owner=request.user)

    if request.method == "POST":
        car_form = CarForm(request.POST, instance=car)
        if car_form.is_valid():
            car_form.save()
            return redirect("cars:car_detail", car_id=car.id)
    else:
        car_form = CarForm(instance=car)

    return render(request, "cars/car_edit.html", {
        "car": car,
        "car_form": car_form,
    })


@login_required
def car_delete(request, car_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    car = get_object_or_404(Car, id=car_id, owner=request.user)
    car.delete()
    return redirect("cars:cars_list")

@login_required
def my_favorites(request):
    favorite_ids = set(
        Favorite.objects.filter(user=request.user).values_list("car_id", flat=True)
    )
    cars = (
        Car.objects.filter(id__in=favorite_ids, is_active=True)
        .prefetch_related("images")
        .order_by("-created_at")
    )
    return render(request, "cars/my_favorites.html", {
        "cars": cars,
        "favorite_ids": favorite_ids,
    })