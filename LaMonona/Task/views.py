from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Empleados, AuthUser, AuthUserGroups, AuthUserUserPermissions, Ventas, Productos, Cajas
from .forms import EmpleadoCreationForm, EditarEmpleadoForm, EditarPerfilForm, CambiarContraseñaForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth,TruncWeek
from django.utils.translation import activate
from django.db.models import Count, Sum
import logging
import json

logger = logging.getLogger(__name__)


def inicio(request):
    return render(request, 'inicio.html')

# Esta vista ahora mostrará la lista de usuarios si el usuario está autenticado
@login_required
def user_list(request):
    empleados = Empleados.objects.all().select_related('id_user')
    return render(request, 'userlist.html', {'empleados': empleados})

# La vista original de combined_charts no es necesaria si userlist_view ya la maneja,
# pero la mantengo por si la necesitas para otro propósito.
def combined_charts(request):
    if request.user.is_authenticated:
        return render(request, 'userlist.html') # Ahora renderiza userlist.html
    else:
        return render(request, 'signin.html')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else: 
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            login(request, user)
            # Redirige a la vista que muestra la lista de usuarios
            return redirect('userlist')
        
def exit(request):
    logout(request)
    return redirect('signin')


@login_required
def user_profile(request):
    auth_user = get_object_or_404(AuthUser, username=request.user.username)
    empleado = get_object_or_404(Empleados, id_user=auth_user)
    edit_form = EditarPerfilForm(instance=empleado)
    password_form = CambiarContraseñaForm()
    return render(request, 'user.html', {
        'empleado': empleado,
        'edit_form': edit_form,
        'password_form': password_form
    })


@login_required
@require_http_methods(["GET", "POST"])
def add_user(request):
    if request.method == 'POST':
        form = EmpleadoCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"El usuario {new_user.nombre} ha sido creado correctamente.")
            return JsonResponse({'success': True, 'message': f"El usuario {new_user.nombre} ha sido creado correctamente."})
        else:
            print(f"Form errors: {form.errors}")  # Add this line for debugging
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EmpleadoCreationForm()
    
    return render(request, 'add_user.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def edit_user(request, user_id):
    empleado = get_object_or_404(Empleados, id_user__id=user_id)
    if request.method == 'POST':
        form = EditarEmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            updated_user = form.save()
            messages.success(request, f"El usuario {updated_user.nombre} ha sido actualizado correctamente.")
            return JsonResponse({'success': True, 'message': f"El usuario {updated_user.nombre} ha sido actualizado correctamente."})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EditarEmpleadoForm(instance=empleado)
    return render(request, 'edit_user.html', {'form': form, 'empleado': empleado})


@login_required
@require_http_methods(["POST"])
def toggle_user_active(request, user_id):
    empleado = get_object_or_404(Empleados, id_user__id=user_id)
    user = empleado.id_user
    user.is_active = not user.is_active
    user.save()
    
    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f"El usuario {empleado.nombre} ha sido {status}.")
    return JsonResponse({'success': True, 'is_active': user.is_active})


@login_required
@require_http_methods(["POST"])
def change_password(request):
    if request.method == 'POST':
        form = CambiarContraseñaForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['password_actual']):
                user.set_password(form.cleaned_data['password_nueva'])
                user.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
                return redirect('user')
            else:
                messages.error(request, 'La contraseña actual es incorrecta.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    return redirect('user')    


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        logger.info("Formulario válido, intentando guardar la nueva contraseña")
        response = super().form_valid(form)
        logger.info("Contraseña guardada exitosamente")
        return response

    def form_invalid(self, form):
        logger.error(f"Formulario inválido. Errores: {form.errors}")
        return super().form_invalid(form)
    

@login_required
@require_http_methods(["POST"])
def edit_profile(request, user_id):
    empleado = get_object_or_404(Empleados, id_user__id=user_id)
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('user')
        else:
            messages.error(request, "Error al actualizar el perfil.")
    return redirect('user')