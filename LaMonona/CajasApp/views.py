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
            form.save()
            return redirect('lista_cajas')
    else:
        form = CajaForm()
    return render(request, 'cajas/form.html', {'form': form})

def editar_caja(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = CajaForm(request.POST, instance=caja)
        if form.is_valid():
            form.save()
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
            # bloqueo para evitar race conditions
            try:
                with transaction.atomic():
                    id_caja = form.cleaned_data['id_caja']
                    # lock rows related to esa caja
                    existing = TurnosCaja.objects.select_for_update().filter(id_caja=id_caja, fecha_cierre__isnull=True)
                    if existing.exists():
                        form.add_error(None, 'Ya hay un turno abierto para esa caja; ciérralo antes de abrir uno nuevo.')
                    else:
                        turno = form.save(commit=False)
                        # opcional: establecer fecha_apertura ahora si no viene
                        if not turno.fecha_apertura:
                            turno.fecha_apertura = timezone.now()
                        turno.save()
                        return redirect('lista_turnos')  # o la url que uses
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = TurnoForm()
    return render(request, 'turnos/form.html', {'form': form})
