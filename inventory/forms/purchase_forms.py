from django import forms
from django.forms import ModelForm
from ..models import Purchase
from ..models import PurchaseItem

class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        fields = [
            'supplier',
            'order_date',
            'expected_delivery_date',
            'delivery_date',
            'order_status',
        ]

        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "expected_delivery_date": forms.DateInput(attrs={"type": "date"}),
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
        }


class PurchaseItemForm(ModelForm):
    class Meta:
        model = PurchaseItem
        fields = [
            'purchase',
            'variant',
            'ordered_quantity',
            'delivered_quantity',
            'unit_cost',
            'discount_percent'
        ]        