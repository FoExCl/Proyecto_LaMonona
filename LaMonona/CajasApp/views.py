from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from Task.models import Cajas, TurnosCaja
from .forms import CajaForm, TurnoForm


def lista_cajas(request):
    cajas = Cajas.objects.all()
    return render(request, 'cajas/lista.html', {'cajas': cajas})


def crear_caja(request):
    if request.method == 'POST':
        form = CajaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    sucursal = form.cleaned_data['id_sucursal']
                    # bloquear todas las cajas de esa sucursal
                    existentes = Cajas.objects.select_for_update().filter(
                        id_sucursal=sucursal,
                        estado='Abierta'
                    )
                    if existentes.exists():
                        form.add_error(None, 'Ya existe una caja abierta en esta sucursal; ciérrala antes de abrir otra.')
                    else:
                        caja = form.save(commit=False)   # 👈 acá
                        if not caja.fecha_apertura:
                            caja.fecha_apertura = timezone.now()
                        caja.id_sucursal = sucursal      # 👈 lo asignás explícito
                        caja.save()
                        return redirect('lista_cajas')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = CajaForm()
    return render(request, 'cajas/form.html', {'form': form})



def editar_caja(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)

    if request.method == 'POST':
        form = CajaForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save(commit=False)   # guardamos sin confirmar para poder modificar
            sucursal = form.cleaned_data.get('id_sucursal')
            if sucursal:
                caja.id_sucursal = sucursal
            caja.save()

            # 🔹 Lógica de turnos
            if caja.estado == "Cerrada":
                turno_abierto = TurnosCaja.objects.filter(
                    id_caja=caja, fecha_cierre__isnull=True
                ).first()
                if turno_abierto:
                    turno_abierto.fecha_cierre = timezone.now()
                    turno_abierto.save()

            elif caja.estado == "Abierta":
                # Creamos un turno si no hay otro abierto
                if not TurnosCaja.objects.filter(id_caja=caja, fecha_cierre__isnull=True).exists():
                    TurnosCaja.objects.create(
                        id_caja=caja,
                        id_empleado=None,  # ⚠️ ajustar si lo ligás a un usuario/empleado
                        fecha_apertura=timezone.now()
                    )

            return redirect('lista_cajas')
    else:
        form = CajaForm(instance=caja)

    return render(request, 'cajas/form.html', {'form': form})

def eliminar_caja(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        caja.delete()
        return redirect('lista_cajas')
    return render(request, 'cajas/eliminar.html', {'caja': caja})


def crear_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    id_caja = form.cleaned_data['id_caja']
                    existentes = TurnosCaja.objects.select_for_update().filter(
                        id_caja=id_caja,
                        fecha_cierre__isnull=True
                    )
                    if existentes.exists():
                        form.add_error(None, 'Ya hay un turno abierto para esa caja; ciérralo antes de abrir uno nuevo.')
                    else:
                        turno = form.save(commit=False)
                        if not turno.fecha_apertura:
                            turno.fecha_apertura = timezone.now()
                        turno.save()
                        return redirect('lista_turnos')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = TurnoForm()
    return render(request, 'cajas/form.html', {'form': form})
