from django import forms
from django.core.exceptions import ValidationError
from Task.models import Cajas,TurnosCaja

UBICACIONES = [
    ('Monona, zn oeste', 'Monona, zn oeste'),
    ('Monona, zn norte', 'Monona, zn norte'),
]

ESTADOS = [
    ('Abierta', 'Abierta'),
    ('Cerrada', 'Cerrada'),
]

class CajaForm(forms.ModelForm):
    ubicacion = forms.ChoiceField(choices=UBICACIONES, widget=forms.Select(attrs={'class': 'form-control'}))
    estado = forms.ChoiceField(choices=ESTADOS, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Cajas
        fields = ['id_sucursal', 'ubicacion', 'estado']
        widgets = {
            'id_sucursal': forms.Select(attrs={'class': 'form-control'}),
        }
        
class TurnoForm(forms.ModelForm):
    class Meta:
        model = TurnosCaja
        # campos que usás para crear un turno
        fields = ['id_caja', 'fecha_apertura', 'fecha_cierre', 'ingresos_totales', 'egresos_totales', 'saldo_final']
        widgets = {
            'id_caja': forms.Select(attrs={'class': 'form-control'}),
            'fecha_apertura': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_cierre': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        id_caja = cleaned.get('id_caja')
        fecha_cierre = cleaned.get('fecha_cierre')

        if id_caja and not fecha_cierre:
            sucursal_id = id_caja.id_sucursal_id  # si Caja tiene FK a Sucursal
            from .models import TurnosCaja

            # Buscar si ya hay turno abierto en la misma sucursal
            qs = TurnosCaja.objects.filter(
                id_caja__id_sucursal_id=sucursal_id,
                fecha_cierre__isnull=True
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    f"Ya existe un turno abierto en la sucursal {id_caja.id_sucursal.nombre}. "
                    "Debe cerrarse antes de abrir otro."
                )

        return cleaned