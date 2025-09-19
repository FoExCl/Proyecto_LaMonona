from django import forms
from Task.models import Ventas

class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = ['id_turno', 'nombre_cliente', 'fecha_venta', 'total_venta']
