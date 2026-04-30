from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Car, CarImage, Favorite, CarViewHistory
from .forms import CarForm
import json

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


def _format_compare_number(value: int) -> str:
    return f"{int(value):,}"


def _build_comparison_rows(cars):
    return [
        {"label": "Marca", "values": [car.make for car in cars]},
        {"label": "Modelo", "values": [car.model for car in cars]},
        {"label": "Año", "values": [str(car.year) for car in cars]},
        {"label": "Precio", "values": [f"$ {_format_compare_number(car.price)}" for car in cars]},
        {"label": "Kilometraje", "values": [f"{_format_compare_number(car.mileage_km)} km" for car in cars]},
        {"label": "Ciudad", "values": [car.city or "Sin ciudad" for car in cars]},
        {"label": "Estado", "values": ["Vendido" if car.is_sold else "Disponible" for car in cars]},
        {"label": "Vendedor", "values": [car.owner.username for car in cars]},
        {
            "label": "Publicado",
            "values": [car.created_at.strftime("%d/%m/%Y") for car in cars],
        },
    ]


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


def compare_cars(request):
    selected_ids = []
    seen_ids = set()

    for raw_id in request.GET.getlist("cars"):
        if raw_id.isdigit():
            car_id = int(raw_id)
            if car_id not in seen_ids:
                seen_ids.add(car_id)
                selected_ids.append(car_id)

    compare_limit = 3
    comparison_error = None
    selected_cars = []

    cars_qs = (
        Car.objects.filter(is_active=True)
        .select_related("owner")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    if len(selected_ids) > compare_limit:
        comparison_error = "Puedes comparar hasta 3 vehículos al mismo tiempo."
    elif selected_ids:
        cars_by_id = {car.id: car for car in cars_qs.filter(id__in=selected_ids)}
        selected_cars = [cars_by_id[car_id] for car_id in selected_ids if car_id in cars_by_id]

        if len(selected_cars) < 2:
            comparison_error = "Selecciona al menos 2 vehículos activos para compararlos."

    comparison_rows = _build_comparison_rows(selected_cars) if len(selected_cars) >= 2 else []

    return render(request, "cars/compare_cars.html", {
        "available_cars": cars_qs,
        "selected_ids": selected_ids,
        "selected_cars": selected_cars,
        "comparison_rows": comparison_rows,
        "comparison_error": comparison_error,
        "compare_limit": compare_limit,
    })


def car_detail(request, car_id: int):
    car = get_object_or_404(
        Car.objects.select_related("owner", "owner__profile").prefetch_related("images"),
        id=car_id,
        is_active=True,
    )

    # Guardar historial de visualización
    if request.user.is_authenticated:
        history, created = CarViewHistory.objects.get_or_create(
            user=request.user,
            car=car,
            defaults={
                "last_viewed_at": timezone.now(),
                "times_viewed": 1,
            }
        )

        if not created:
            history.last_viewed_at = timezone.now()
            history.times_viewed += 1
            history.save(update_fields=["last_viewed_at", "times_viewed"])

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

from django.contrib.auth.decorators import login_required

@login_required
def viewed_history(request):
    history = CarViewHistory.objects.filter(
        user=request.user,
        car__is_active=True
    ).select_related("car")

    return render(request, "cars/history.html", {
        "history": history
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
def toggle_sold(request, car_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    car = get_object_or_404(Car, id=car_id, owner=request.user)

    if car.is_sold:
        car.is_sold = False
        car.sold_at = None
    else:
        car.is_sold = True
        car.sold_at = timezone.now()

    car.save(update_fields=["is_sold", "sold_at"])

    back = request.META.get("HTTP_REFERER")
    return redirect(back or "cars:car_detail", car_id=car.id)


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

def map_view(request):
    CITY_COORDS = {
        "bogotá":        (4.7110, -74.0721),
        "bogota":        (4.7110, -74.0721),
        "medellín":      (6.2442, -75.5812),
        "medellin":      (6.2442, -75.5812),
        "cali":          (3.4516, -76.5320),
        "barranquilla":  (10.9685, -74.7813),
        "cartagena":     (10.3910, -75.4794),
        "bucaramanga":   (7.1193, -73.1227),
        "pereira":       (4.8087, -75.6906),
        "santa marta":   (11.2408, -74.1990),
        "santamarta":    (11.2408, -74.1990),
        "manizales":     (5.0703, -75.5138),
        "cúcuta":        (7.8939, -72.5078),
        "cucuta":        (7.8939, -72.5078),
        "ibagué":        (4.4389, -75.2322),
        "ibague":        (4.4389, -75.2322),
        "neiva":         (2.9273, -75.2819),
        "villavicencio": (4.1420, -73.6266),
        "pasto":         (1.2136, -77.2811),
        "montería":      (8.7575, -75.8857),
        "monteria":      (8.7575, -75.8857),
        "popayán":       (2.4448, -76.6147),
        "popayan":       (2.4448, -76.6147),
        "sincelejo":     (9.3047, -75.3978),
        "valledupar":    (10.4631, -73.2532),
        "armenia":       (4.5339, -75.6811),
        "riohacha":      (11.5444, -72.9072),
    }

    active_cars = (
        Car.objects.filter(is_active=True)
        .select_related("owner")
        .prefetch_related("images")
        .exclude(city="")
    )

    # Agrupar por ciudad
    city_data = {}
    for car in active_cars:
        city_key = car.city.lower().strip()
        coords = CITY_COORDS.get(city_key)
        if not coords:
            continue

        if city_key not in city_data:
            city_data[city_key] = {
                "name":   car.city,
                "lat":    coords[0],
                "lng":    coords[1],
                "cars":   [],
            }

        first_image = car.images.first()
        city_data[city_key]["cars"].append({
            "id":    car.id,
            "make":  car.make,
            "model": car.model,
            "year":  car.year,
            "price": f"${car.price:,}",
            "url":   car.get_url(),
            "image": first_image.image.url if first_image else None,
        })

    cities_json = json.dumps(list(city_data.values()))

    return render(request, "cars/map.html", {
        "cities_json": cities_json,
        "total_cars":  active_cars.count(),
    })