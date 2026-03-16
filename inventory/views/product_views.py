from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from ..models import Product
from ..forms.product_forms import ProductForm

class ProductListView(ListView):
  model = Product
  template_name = "inventory/products/product_list.html"
  context_object_name = "products"


class ProductCreateView(CreateView):
  model = Product
  form_class = ProductForm
  template_name = "inventory/products/product_form.html"
  success_url = "/products/"

class ProductUpdateView(UpdateView):
  model = Product
  form_class = ProductForm
  template_name = "inventory/products/product_form.html"
  success_url = reverse_lazy("product_list")  

class ProductDeleteView(DeleteView):
  model = Product
  template_name = "inventory/products/product_confirm_delete.html"
  success_url = reverse_lazy("product_list")  