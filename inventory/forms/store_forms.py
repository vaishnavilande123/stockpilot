from django.forms import ModelForm
from ..models import Store
from django import forms

class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ['store_name', 'location']

        widgets = {
         'store_name': forms.TextInput(attrs={'class': 'form-control'}),
         'location': forms.TextInput(attrs={'class': 'form-control'}),
        }    

      