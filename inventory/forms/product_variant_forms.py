from django.forms import ModelForm
from ..models import ProductVariant

class ProductVariantForm(ModelForm):
  class Meta:
    model = ProductVariant
    fields = ['product', 'size', 'color']