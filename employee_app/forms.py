from django import forms
from django.utils.translation import gettext_lazy as _
from .models import TimeRecord, Employee
from django.forms import DateInput, TextInput
from typing import Any, Dict


class TimeRecordForm(forms.ModelForm):
    class Meta:
        model = TimeRecord
        fields = ['employee', 'date', 'time_in', 'time_out', 'lunch_time']
        labels = {
            'employee': _('Employee'),
            'date': _('Date'),
            'time_in': _('Time In'),
            'time_out': _('Time Out'),
            'lunch_time': _('Lunch Time'),
        }
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'time_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lunch_time': TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')
        lunch_time = cleaned_data.get('lunch_time')

        if time_out and time_in:
            if time_out < time_in:
                self.add_error('time_out', _('Time Out must be after Time In.'))
            elif time_out == time_in:
                self.add_error('time_out', _('Time Out cannot be the same as Time In.'))

        if lunch_time and lunch_time.total_seconds() < 0:
            self.add_error('lunch_time', _('Lunch time cannot be negative.'))

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """Initialize the form and make certain fields optional."""
        super().__init__(*args, **kwargs)
        self.fields['time_in'].required = False
        self.fields['time_out'].required = False
        self.fields['lunch_time'].required = False