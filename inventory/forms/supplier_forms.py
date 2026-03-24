from django.forms import ModelForm
from ..models import Supplier

class SupplierForm(ModelForm):
  class Meta:
    model = Supplier
    fields = [
            'supplier_name',
            'phone',
            'email',
            'city',
            'address'
        ]