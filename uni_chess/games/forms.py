from datetime import date
from django.forms import ModelForm, DateInput, TimeInput, TextInput, HiddenInput
from django.core.exceptions import ValidationError
from .models import Game, Tournament
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'minimum_players', 'maximum_players', 'prize', 'duration', 'increment']


class AddPlayerForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.none(), label='Select a player')

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament', None)
        super(AddPlayerForm, self).__init__(*args, **kwargs)
        if tournament:
            self.fields['user'].queryset = User.objects.exclude(username__in=tournament.players)


class RemovePlayerForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.none(), label='Select a player')

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament', None)
        super(RemovePlayerForm, self).__init__(*args, **kwargs)
        if tournament:
            self.fields['user'].queryset = User.objects.filter(username__in=tournament.players)

