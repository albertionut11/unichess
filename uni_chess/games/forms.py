from datetime import date

from django.forms import ModelForm, DateInput, TimeInput, TextInput
from django.core.exceptions import ValidationError

from .models import Game


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = [field.name for field in Game._meta.fields if field.name != 'data']
        widgets = {
            'date': DateInput(attrs={"type": "date"}),
            'start': TimeInput(attrs={"type": "time"}),
            'result': TextInput(attrs={"type": "number", "min": "0", "max": "2"}),
        }

    def clean_date(self):
        d = self.cleaned_data.get("date")
        if d < date.today():
            raise ValidationError("Games cannot be in the past")
        return d
