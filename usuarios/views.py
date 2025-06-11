# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Importa las funciones de autenticación
from django.contrib.auth.forms import AuthenticationForm # Formulario de login de Django
from django.contrib.auth.decorators import login_required # Decorador para vistas protegidas
from django.urls import reverse_lazy # Para redirigir después del logout

# Para el registro (necesitarás crear un UserCreationForm personalizado si quieres más campos)
from django.contrib.auth.forms import UserCreationForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirigir a la página anterior o a una por defecto
                next_url = request.POST.get('next') or request.GET.get('next') or reverse_lazy('blog_circadiano:lista_articulos')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    # Obtener el parámetro 'next' para redirigir después del login
    next_url = request.GET.get('next', '') # Por si viene de un @login_required

    return render(request, 'usuarios/login.html', {'form': form, 'next': next_url})

@login_required(login_url='/usuarios/login/') # Asegúrate de que esta URL exista
def logout_view(request):
    logout(request)
    # Redirigir a la página principal o a la página de login
    return redirect('blog_circadiano:lista_articulos') # O a una página de 'logout_success' si la creas

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # Formulario de registro básico de Django
        if form.is_valid():
            form.save()
            return redirect('usuarios:login') # Redirigir al login después del registro exitoso
    else:
        form = UserCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})