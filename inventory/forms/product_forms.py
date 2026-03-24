from django.forms import ModelForm
from ..models import Product, ProductVariant

class ProductForm(ModelForm):
  class Meta:
    model = Product
    exclude = ["store","created_at"]

