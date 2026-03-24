from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import Sale, SaleItem, ProductVariant, Store
from ..forms.sale_forms import SaleForm, SaleItemForm
from .landing_views import StoreRequiredMixin

# =========================
# HELPER FUNCTION
# =========================
def get_current_store(request):
    store_id = request.session.get("store_id")
    return get_object_or_404(Store, id=store_id)


# =========================
# SALE VIEWS
# =========================

class SaleListView(StoreRequiredMixin, ListView):
    model = Sale
    template_name = "inventory/sales/sale_list.html"
    context_object_name = "sales"

    def get_queryset(self):
        store = get_current_store(self.request)
        return Sale.objects.filter(store=store)


class SaleCreateView(StoreRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "inventory/sales/sale_form.html"
    success_url = reverse_lazy("sale_list")

    def form_valid(self, form):
        form.instance.store = get_current_store(self.request)
        return super().form_valid(form)


# =========================
# SALE ITEM VIEWS
# =========================

class SaleItemListView(StoreRequiredMixin,ListView):
    model = SaleItem
    template_name = "inventory/sales/sale_item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        store = get_current_store(self.request)

        sale_id = self.request.GET.get("sale_id")

        if sale_id:
            return SaleItem.objects.filter(
                sale_id=sale_id,
                sale__store=store
            )

        return SaleItem.objects.filter(sale__store=store)


class SaleItemCreateView(StoreRequiredMixin,CreateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = "inventory/sales/sale_item_form.html"
    success_url = reverse_lazy("sale_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        store = get_current_store(self.request)

        # show only sales of this store
        form.fields["sale"].queryset = Sale.objects.filter(store=store)

        # show only variants of this store
        form.fields["variant"].queryset = ProductVariant.objects.filter(
            product__store=store
        )

        # existing logic
        sale_id = self.request.GET.get("sale_id")

        if sale_id:
            form.initial["sale"] = sale_id
            form.fields["sale"].disabled = True

        return form


class SaleItemUpdateView(StoreRequiredMixin,UpdateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = "inventory/sales/sale_item_form.html"
    success_url = reverse_lazy("sale_list")

    def get_queryset(self):
        store = get_current_store(self.request)
        return SaleItem.objects.filter(sale__store=store)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        store = get_current_store(self.request)

        form.fields["sale"].queryset = Sale.objects.filter(store=store)
        form.fields["variant"].queryset = ProductVariant.objects.filter(
            product__store=store
        )

        return form


class SaleItemDeleteView(StoreRequiredMixin, DeleteView):
    model = SaleItem
    template_name = "inventory/sales/sale_item_confirm_delete.html"
    success_url = reverse_lazy("sale_list")

    def get_queryset(self):
        store = get_current_store(self.request)
        return SaleItem.objects.filter(sale__store=store)