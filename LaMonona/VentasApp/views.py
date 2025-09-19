from django.shortcuts import render, redirect, get_object_or_404
from Task.models import Ventas
from .forms import VentaForm

def lista_ventas(request):
    ventas = Ventas.objects.all()
    return render(request, 'ventas/lista.html', {'ventas': ventas})

def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ventas')
    else:
        form = VentaForm()
    return render(request, 'ventas/form.html', {'form': form})

def editar_venta(request, pk):
    venta = get_object_or_404(Ventas, pk=pk)
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('lista_ventas')
    else:
        form = VentaForm(instance=venta)
    return render(request, 'ventas/form.html', {'form': form})

def eliminar_venta(request, pk):
    venta = get_object_or_404(Ventas, pk=pk)
    if request.method == 'POST':
        venta.delete()
        return redirect('lista_ventas')
    return render(request, 'ventas/eliminar.html', {'venta': venta})
