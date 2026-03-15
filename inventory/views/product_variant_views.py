from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from ..models import ProductVariant
from ..forms.product_variant_forms import ProductVariantForm

class ProductVariantListView(ListView):
  model = ProductVariant
  template_name = "inventory/product_variants/product_variant_list.html"
  context_object_name = 'product_variants'

class ProductVariantCreateView(CreateView): 
  model = ProductVariant
  template_name = "inventory/product_variants/product_variant_form.html"
  form_class = ProductVariantForm
  success_url = reverse_lazy('product_variant_list')

  def get_form(self, form_class=None):
    form = super().get_form(form_class)

    product_id = self.request.GET.get('product_id')

    if product_id:
        form.initial['product'] = product_id
        form.fields['product'].disabled = True

    return form

  

class ProductVariantUpdateView(UpdateView): 
  model = ProductVariant
  template_name = "inventory/product_variants/product_variant_form.html"
  form_class = ProductVariantForm
  success_url = reverse_lazy('product_variant_list')

class ProductVariantDeleteView(DeleteView): 
  model = ProductVariant
  template_name = "inventory/product_variants/product_variant_confirm_delete.html"
  success_url = reverse_lazy('product_variant_list')    