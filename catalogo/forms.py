from django import forms
from .models import Titulo


class ValoracionForm(forms.ModelForm):
    class Meta:
        model = Titulo
        fields = ['estado', 'mi_nota', 'fecha_vista', 'comentario']
        labels = {'mi_nota': 'Mi calificación (1-10)', 'fecha_vista': 'Fecha en que la vi'}
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'mi_nota': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'fecha_vista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }