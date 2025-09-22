from django import forms
from Task.models import Ventas, TurnosCaja
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from crispy_forms.bootstrap import FormActions

class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = ['id_turno', 'nombre_cliente', 'fecha_venta', 'total_venta']
        widgets = {
            'fecha_venta': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'total_venta': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'nombre_cliente': forms.TextInput(attrs={'placeholder': 'Nombre del cliente'}),
        }
        labels = {
            'id_turno': 'Turno de Caja',
            'nombre_cliente': 'Nombre del Cliente',
            'fecha_venta': 'Fecha de Venta',
            'total_venta': 'Total de la Venta (MXN)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('id_turno', css_class='form-select'),
                Field('nombre_cliente', css_class='form-control'),
                Field('fecha_venta', css_class='form-control'),
                Field('total_venta', css_class='form-control'),
                css_class='row'
            ),
            FormActions(
                Submit('submit', '💾 Guardar Venta', css_class='btn btn-primary'),
            )
        )
