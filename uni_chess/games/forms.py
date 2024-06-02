from datetime import date
from django.forms import ModelForm, DateInput, TimeInput, TextInput, HiddenInput
from django.core.exceptions import ValidationError
from .models import Game


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ['white', 'black', 'duration', 'increment']
        widgets = {
            'duration': TextInput(attrs={"type": "number", "min": "1"}),
            'increment': TextInput(attrs={"type": "number", "min": "0"}),
        }

    def clean_date(self):
        d = self.cleaned_data.get("date")
        if d < date.today():
            raise ValidationError("Games cannot be in the past")
        return d
