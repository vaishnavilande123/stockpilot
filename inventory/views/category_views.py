from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..forms.category_form import CategoryForm
from ..models import Category

class CategoryListView(ListView):
  model = Category
  template_name='inventory/categories/category_list.html'
  context_object_name = 'categories'


class CategoryCreateView(CreateView):
  model = Category
  form_class = CategoryForm
  template_name = 'inventory/categories/category_form.html'
  success_url = reverse_lazy('category_list')

class CategoryUpdateView(UpdateView):
  model = Category
  form_class = CategoryForm
  template_name = 'inventory/categories/category_form.html'
  success_url = reverse_lazy('category_list')

class CategoryDeleteView(DeleteView):
  model = Category
  template_name = 'inventory/categories/category_confirm_delete.html'  
  success_url = reverse_lazy('category_list')