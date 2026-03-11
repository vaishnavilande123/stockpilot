from django.forms import ModelForm
from ..models import Product, ProductVariant

class ProductForm(ModelForm):
  class Meta:
    model = Product
    exclude = ["created_at"]


class ProductVariantForm(ModelForm):
  class Meta:
    model = ProductVariant
    fields = "__all__"