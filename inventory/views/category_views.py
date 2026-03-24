from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..forms.category_form import CategoryForm
from ..models import Category, Store
from django.shortcuts import get_object_or_404, redirect
from .landing_views import StoreRequiredMixin
# =========================
# HELPER FUNCTION
# =========================


def get_current_store(request):
    store_id = request.session.get("store_id")
    if not store_id:
        redirect('store_selection')
    return get_object_or_404(Store, id=store_id)


# =========================
# LIST VIEW
# =========================
class CategoryListView(StoreRequiredMixin, ListView):
    model = Category
    template_name = 'inventory/categories/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        store = get_current_store(self.request)
        return Category.objects.filter(store=store)


# =========================
# CREATE VIEW
# =========================
class CategoryCreateView(StoreRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/categories/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.store = get_current_store(self.request)
        return super().form_valid(form)


# =========================
# UPDATE VIEW
# =========================
class CategoryUpdateView(StoreRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/categories/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        store = get_current_store(self.request)
        return Category.objects.filter(store=store)


# =========================
# DELETE VIEW
# =========================
class CategoryDeleteView(StoreRequiredMixin, DeleteView):
    model = Category
    template_name = 'inventory/categories/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        store = get_current_store(self.request)
        return Category.objects.filter(store=store)