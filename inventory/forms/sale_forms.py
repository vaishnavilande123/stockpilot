from django import forms
from django.forms import ModelForm
from ..models import Sale


class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = [
            "store",
            "sale_date",
            "total_amount"
        ]

        widgets = {
            "sale_date": forms.DateInput(attrs={"type": "date"})
        }

from ..models import SaleItem


class SaleItemForm(ModelForm):
    class Meta:
        model = SaleItem
        fields = [
            "sale",
            "variant",
            "quantity",
            "selling_price"
        ]        