from django import forms
from .models import Report


class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': (
                    'w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                    'dark:border-slate-700 dark:bg-slate-900 dark:text-white'
                ),
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe brevemente el problema (opcional)…',
                'class': (
                    'w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm '
                    'resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 '
                    'dark:border-slate-700 dark:bg-slate-900 dark:text-white'
                ),
            }),
        }
        labels = {
            'reason':      'Motivo del reporte',
            'description': 'Descripción adicional',
        }
