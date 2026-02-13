from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm, UserForm
from django.contrib import messages  
from .models import Profile

# ------------------------------
# LOGIN
# ------------------------------
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.user.is_authenticated:
        return redirect(next_url or 'catalogo')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(next_url or 'home')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'next': next_url,
    }
    return render(request, 'account/login.html', context)


# ------------------------------
# REGISTER
# ------------------------------
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Guardar datos adicionales en el perfil
            profile, created = Profile.objects.get_or_create(user=user)
            profile.telefono = form.cleaned_data.get('telefono')
            profile.ciudad = form.cleaned_data.get('ciudad_residencia')
            profile.save()

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'account/register.html', {'form': form})

@login_required
def home(request):
    profile = getattr(request.user, "profile", None)

    return render(request, "account/home.html", {
        "username": request.user.username,
        "ciudad": profile.ciudad if profile else None
    })


