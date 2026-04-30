import random
import time

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings as django_settings

from .forms import RegisterForm, ProfileEditForm, VerifyCodeForm
from .models import Profile
from cars.models import Car, Favorite

VERIFY_EXPIRY_SECONDS = 600
MAX_ATTEMPTS          = 3


def _generate_code():
    return str(random.randint(100000, 999999))


def _send_verification_email(email, code):
    send_mail(
        subject="Tu código de verificación — CarVRuuum",
        message=(
            f"Hola,\n\n"
            f"Tu código de verificación es: {code}\n\n"
            f"Este código expira en 10 minutos.\n"
            f"Si no solicitaste esto, ignora este correo.\n\n"
            f"— El equipo de CarVRuuum"
        ),
        from_email=django_settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


# ────────────────────────────────────────────────────────────────
def landing(request):
    total_cars = Car.objects.filter(is_active=True).count()

    my_cars_count      = 0
    my_favorites_count = 0
    if request.user.is_authenticated:
        my_cars_count      = Car.objects.filter(owner=request.user).count()
        my_favorites_count = Favorite.objects.filter(user=request.user).count()

    return render(request, "account/landing.html", {
        "total_cars":         total_cars,
        "my_cars_count":      my_cars_count,
        "my_favorites_count": my_favorites_count,
    })


# ────────────────────────────────────────────────────────────────
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.user.is_authenticated:
        return redirect(next_url or "profile")  # ← corregido

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            code = _generate_code()
            request.session["pending_login_user_id"]         = user.pk
            request.session["pending_login_next"]             = next_url or ""
            request.session["login_verification_code"]        = code
            request.session["login_verification_timestamp"]   = time.time()
            request.session["login_verification_attempts"]    = 0

            _send_verification_email(user.email, code)
            return redirect("verify_login")
    else:
        form = AuthenticationForm()

    return render(request, "account/login.html", {"form": form, "next": next_url})


# ────────────────────────────────────────────────────────────────
def verify_login_view(request):
    user_id = request.session.get("pending_login_user_id")
    if not user_id:
        return redirect("login")

    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect("login")

    form    = VerifyCodeForm()
    error   = None
    expired = False

    elapsed = time.time() - request.session.get("login_verification_timestamp", 0)
    if elapsed > VERIFY_EXPIRY_SECONDS:
        expired = True

    if request.method == "POST":

        if "resend" in request.POST:
            code = _generate_code()
            request.session["login_verification_code"]      = code
            request.session["login_verification_timestamp"] = time.time()
            request.session["login_verification_attempts"]  = 0
            _send_verification_email(user.email, code)
            return redirect("verify_login")

        form     = VerifyCodeForm(request.POST)
        attempts = request.session.get("login_verification_attempts", 0)

        if expired:
            error = "El código ha expirado. Por favor solicita uno nuevo."

        elif attempts >= MAX_ATTEMPTS:
            error = "Demasiados intentos fallidos. Solicita un nuevo código."

        elif form.is_valid():
            entered = form.cleaned_data["code"].strip()
            correct = request.session.get("login_verification_code", "")

            if entered == correct:
                next_url = request.session.get("pending_login_next") or "profile"  # ← corregido

                for key in ["pending_login_user_id", "pending_login_next",
                            "login_verification_code", "login_verification_timestamp",
                            "login_verification_attempts"]:
                    request.session.pop(key, None)

                login(request, user)
                return redirect(next_url)

            else:
                attempts += 1
                request.session["login_verification_attempts"] = attempts
                remaining = MAX_ATTEMPTS - attempts
                if remaining > 0:
                    error = f"Código incorrecto. Te quedan {remaining} intento{'s' if remaining != 1 else ''}."
                else:
                    error = "Demasiados intentos fallidos. Solicita un nuevo código."

    email        = user.email
    parts        = email.split("@")
    visible      = parts[0][:3]
    masked_email = f"{visible}***@{parts[1]}" if len(parts) == 2 else email

    return render(request, "account/verify_login.html", {
        "form":         form,
        "masked_email": masked_email,
        "error":        error,
        "expired":      expired,
    })


# ────────────────────────────────────────────────────────────────
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            code = _generate_code()
            request.session["pending_registration"] = {
                "username": form.cleaned_data["username"],
                "email":    form.cleaned_data["email"],
                "password": form.cleaned_data["password1"],
                "telefono": form.cleaned_data.get("telefono", ""),
                "ciudad":   form.cleaned_data.get("ciudad_residencia", ""),
            }
            request.session["email_verification_code"]      = code
            request.session["email_verification_timestamp"] = time.time()
            request.session["email_verification_attempts"]  = 0

            _send_verification_email(form.cleaned_data["email"], code)
            return redirect("verify_email")
    else:
        form = RegisterForm()

    return render(request, "account/register.html", {"form": form})


# ────────────────────────────────────────────────────────────────
def verify_email_view(request):
    pending = request.session.get("pending_registration")
    if not pending:
        return redirect("register")

    form    = VerifyCodeForm()
    error   = None
    expired = False

    elapsed = time.time() - request.session.get("email_verification_timestamp", 0)
    if elapsed > VERIFY_EXPIRY_SECONDS:
        expired = True

    if request.method == "POST":

        if "resend" in request.POST:
            code = _generate_code()
            request.session["email_verification_code"]      = code
            request.session["email_verification_timestamp"] = time.time()
            request.session["email_verification_attempts"]  = 0
            _send_verification_email(pending["email"], code)
            return redirect("verify_email")

        form     = VerifyCodeForm(request.POST)
        attempts = request.session.get("email_verification_attempts", 0)

        if expired:
            error = "El código ha expirado. Por favor reenvía uno nuevo."

        elif attempts >= MAX_ATTEMPTS:
            error = "Demasiados intentos fallidos. Solicita un nuevo código."

        elif form.is_valid():
            entered = form.cleaned_data["code"].strip()
            correct = request.session.get("email_verification_code", "")

            if entered == correct:
                from django.contrib.auth.models import User
                user = User.objects.create_user(
                    username=pending["username"],
                    email=pending["email"],
                    password=pending["password"],
                )
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.telefono = pending.get("telefono", "")
                profile.ciudad   = pending.get("ciudad", "")
                profile.save()

                for key in ["pending_registration", "email_verification_code",
                            "email_verification_timestamp", "email_verification_attempts"]:
                    request.session.pop(key, None)

                login(request, user)
                return redirect("profile")  # ← corregido

            else:
                attempts += 1
                request.session["email_verification_attempts"] = attempts
                remaining = MAX_ATTEMPTS - attempts
                if remaining > 0:
                    error = f"Código incorrecto. Te quedan {remaining} intento{'s' if remaining != 1 else ''}."
                else:
                    error = "Demasiados intentos fallidos. Solicita un nuevo código."

    return render(request, "account/verify_email.html", {
        "form":    form,
        "email":   pending["email"],
        "error":   error,
        "expired": expired,
    })


# ────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    my_cars      = Car.objects.filter(owner=request.user, is_active=True).order_by("-created_at")
    my_favorites = Favorite.objects.filter(user=request.user).select_related("car").order_by("-id")

    edit_open = False

    if request.method == "POST":
        form = ProfileEditForm(request.POST, profile=profile)
        if form.is_valid():
            profile.telefono = form.cleaned_data["telefono"]
            profile.ciudad   = form.cleaned_data["ciudad"]
            profile.save()
            return redirect("profile")
        else:
            edit_open = True
    else:
        form = ProfileEditForm(profile=profile)

    return render(request, "account/profile.html", {
        "user_obj":     request.user,
        "profile":      profile,
        "my_cars":      my_cars,
        "my_favorites": my_favorites,
        "form":         form,
        "edit_open":    edit_open,
    })