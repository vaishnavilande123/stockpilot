from django import forms
from django.forms import ModelForm
from ..models import Sale
from ..models import SaleItem

class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = [
            "sale_date",
        ]

        widgets = {
            "sale_date": forms.DateInput(attrs={"type": "date"})
        }


class SaleItemForm(ModelForm):
    class Meta:
        model = SaleItem
        fields = [
            "sale",
            "variant",
            "quantity",
            "selling_price"
        ]        