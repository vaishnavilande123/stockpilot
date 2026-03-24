from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import Supplier, Store
from ..forms.supplier_forms import SupplierForm
from .landing_views import StoreRequiredMixin

# =========================
# HELPER FUNCTION
# =========================
def get_current_store(request):
    store_id = request.session.get("store_id")
    return get_object_or_404(Store, id=store_id)


# =========================
# LIST VIEW
# =========================
class SupplierListView(StoreRequiredMixin, ListView):
    model = Supplier
    template_name = "inventory/suppliers/supplier_list.html"
    context_object_name = "suppliers"

    def get_queryset(self):
        store = get_current_store(self.request)
        return Supplier.objects.filter(store=store)


# =========================
# CREATE VIEW
# =========================
class SupplierCreateView(StoreRequiredMixin,CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/suppliers/supplier_form.html"
    success_url = reverse_lazy("supplier_list")

    def form_valid(self, form):
        form.instance.store = get_current_store(self.request)
        return super().form_valid(form)


# =========================
# UPDATE VIEW
# =========================
class SupplierUpdateView(StoreRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/suppliers/supplier_form.html"
    success_url = reverse_lazy("supplier_list")

    def get_queryset(self):
        store = get_current_store(self.request)
        return Supplier.objects.filter(store=store)


# =========================
# DELETE VIEW
# =========================
class SupplierDeleteView(StoreRequiredMixin,DeleteView):
    model = Supplier
    template_name = "inventory/suppliers/supplier_confirm_delete.html"
    success_url = reverse_lazy("supplier_list")

    def get_queryset(self):
        store = get_current_store(self.request)
        return Supplier.objects.filter(store=store)