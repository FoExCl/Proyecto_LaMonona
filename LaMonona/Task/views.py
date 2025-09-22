from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Empleados, AuthUser, AuthUserGroups, AuthUserUserPermissions, Ventas, Productos, Cajas
from .forms import EmpleadoCreationForm, EditarEmpleadoForm, EditarPerfilForm, CambiarContraseñaForm, ProductoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
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
from django.db.models import Count, Sum, F
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def inicio(request):
    try:
        # Obtenemos el AuthUser desde tu tabla
        auth_user = AuthUser.objects.get(username=request.user.username)

        # Buscamos si es empleado
        Empleados.objects.get(id_user=auth_user)
        # Si existe → es empleado
        return redirect('lista_cajas')

    except AuthUser.DoesNotExist:
        # Esto casi nunca pasa
        messages.error(request, "Usuario no existe en AuthUser")
        return redirect('signin')

    except Empleados.DoesNotExist:
        # No es empleado → admin
        return redirect('userlist')

# Esta vista ahora mostrará la lista de usuarios si el usuario está autenticado

@login_required
def user_list(request):
    # Muestra todos los usuarios (admins)
    users = AuthUser.objects.all()
    return render(request, 'userlist.html', {'users': users})


# La vista original de combined_charts no es necesaria si userlist_view ya la maneja,
# pero la mantengo por si la necesitas para otro propósito.
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')  # redirige a la vista de inicio según rol
        else:
            messages.error(request, "Usuario o contraseña incorrecta")
    return render(request, 'signin.html')
        
@login_required
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
    if not request.user.is_staff:
        raise PermissionDenied("Solo los administradores pueden crear usuarios.")

    if request.method == 'POST':
        form = EmpleadoCreationForm(request.POST)
        if form.is_valid():
            rol = form.cleaned_data.get('rol')
            # Solo superuser puede crear administradores
            if rol == 'administrador' and not request.user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'errors': {'rol': ['Solo los super administradores pueden crear administradores.']}
                })

            empleado = form.save(commit=True)
            return JsonResponse({
                'success': True,
                'message': f"Usuario {empleado.nombre} creado correctamente."
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EmpleadoCreationForm()

    return render(request, 'add_user.html', {'form': form})



@login_required
@require_http_methods(["GET", "POST"])
def edit_user(request, user_id):
    try:
        empleado = Empleados.objects.get(id_user__id=user_id)
    except Empleados.DoesNotExist:
        return JsonResponse({'success': False, 'errors': 'Empleado no encontrado.'})

    if request.method == 'POST':
        form = EditarEmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'Usuario {empleado.nombre} actualizado correctamente.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EditarEmpleadoForm(instance=empleado)

    return render(request, 'edit_user.html', {'form': form})

@login_required
@require_http_methods(["POST"])
def toggle_user_active(request, user_id):
    # Solo administradores pueden cambiar el estado de usuarios
    if not request.user.is_staff:
        raise PermissionDenied("Solo los administradores pueden cambiar el estado de usuarios.")
    
    # No permitir cambiar el estado de uno mismo
    if str(request.user.id) == str(user_id):
        return JsonResponse({'success': False, 'error': 'No puedes cambiar tu propio estado.'})
    
    empleado = get_object_or_404(Empleados, id_user__id=user_id)
    user = empleado.id_user
    
    # No permitir desactivar super administradores si no eres super administrador
    if user.is_superuser and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No puedes cambiar el estado de un super administrador.'})
    
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
    
    # Solo el propietario del perfil o un administrador pueden editarlo
    if str(request.user.id) != str(user_id) and not request.user.is_staff:
        raise PermissionDenied("Solo puedes editar tu propio perfil o ser administrador.")
    
    # No permitir que no-super administradores editen super administradores
    if empleado.id_user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("No puedes editar el perfil de un super administrador.")
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('user')
        else:
            messages.error(request, "Error al actualizar el perfil.")
    return redirect('user')


# ===== VISTAS PARA GESTIÓN DE PRODUCTOS Y STOCK =====

@login_required
def lista_productos(request):
    """Lista todos los productos con alertas de stock bajo"""
    productos = Productos.objects.all().order_by('nombre_producto')
    productos_bajo_stock = productos.filter(stock__lte=F('stock_minimo'))
    productos_sin_stock = productos.filter(stock=0)
    
    context = {
        'productos': productos,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_sin_stock': productos_sin_stock,
        'alertas_count': productos_bajo_stock.count(),
    }
    return render(request, 'productos/lista.html', context)

@login_required
@permission_required('Task.add_productos', raise_exception=True)
def crear_producto(request):
    """Crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" creado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al crear el producto. Verifica los datos.')
    else:
        form = ProductoForm()
    
    return render(request, 'productos/form.html', {'form': form, 'title': 'Nuevo Producto'})

@login_required
@permission_required('Task.change_productos', raise_exception=True)
def editar_producto(request, producto_id):
    """Editar un producto existente"""
    producto = get_object_or_404(Productos, id_producto=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto_editado = form.save()
            messages.success(request, f'Producto "{producto_editado.nombre_producto}" actualizado exitosamente.')
            
            # Verificar si el stock está bajo después de la edición
            if producto_editado.necesita_restock:
                messages.warning(request, f'¡ALERTA! El producto "{producto_editado.nombre_producto}" tiene stock bajo ({producto_editado.stock} unidades).')
            
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al actualizar el producto. Verifica los datos.')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'productos/form.html', {
        'form': form, 
        'title': f'Editar Producto: {producto.nombre_producto}',
        'producto': producto
    })

@login_required
@permission_required('Task.delete_productos', raise_exception=True)
def eliminar_producto(request, producto_id):
    """Eliminar un producto"""
    producto = get_object_or_404(Productos, id_producto=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre_producto
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('lista_productos')
    
    return render(request, 'productos/eliminar.html', {'producto': producto})

@login_required
def dashboard_stock(request):
    """Dashboard con alertas de stock y estadísticas"""
    
    productos_total = Productos.objects.count()
    productos_bajo_stock = Productos.objects.filter(stock__lte=F('stock_minimo'))
    productos_sin_stock = Productos.objects.filter(stock=0)
    productos_stock_normal = Productos.objects.filter(stock__gt=F('stock_minimo'))
    
    # Productos que más necesitan restock (ordenados por diferencia entre stock y stock_minimo)
    productos_criticos = productos_bajo_stock.extra(
        select={'diferencia': 'stock_minimo - stock'}
    ).order_by('-diferencia')[:5]
    
    context = {
        'productos_total': productos_total,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_normal': productos_stock_normal,
        'productos_criticos': productos_criticos,
        'alertas_count': productos_bajo_stock.count(),
        'sin_stock_count': productos_sin_stock.count(),
    }
    
    return render(request, 'productos/dashboard.html', context)