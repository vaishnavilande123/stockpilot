from django.forms import ModelForm
from ..models import Purchase


class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        fields = [
            'store',
            'supplier',
            'order_date',
            'expected_delivery_date',
            'delivery_date',
            'order_status',
            'total_cost'
        ]

from ..models import PurchaseItem


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