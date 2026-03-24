from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import Purchase, PurchaseItem, Supplier, ProductVariant, Store
from ..forms.purchase_forms import PurchaseForm, PurchaseItemForm
from .landing_views import StoreRequiredMixin

# =========================
# HELPER FUNCTION
# =========================
def get_current_store(request):
    store_id = request.session.get("store_id")
    return get_object_or_404(Store, id=store_id)


# =========================
# PURCHASE VIEWS
# =========================

class PurchaseListView(StoreRequiredMixin, ListView):
    model = Purchase
    template_name = "inventory/purchases/purchase_list.html"
    context_object_name = "purchases"

    def get_queryset(self):
        return Purchase.objects.filter(store=get_current_store(self.request))


class PurchaseCreateView(StoreRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "inventory/purchases/purchase_form.html"
    success_url = reverse_lazy("purchase_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        store = get_current_store(self.request)
        form.fields["supplier"].queryset = Supplier.objects.filter(store=store)
        return form

    def form_valid(self, form):
        form.instance.store = get_current_store(self.request)
        return super().form_valid(form)


class PurchaseUpdateView(StoreRequiredMixin, UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "inventory/purchases/purchase_form.html"
    success_url = reverse_lazy("purchase_list")

    def get_queryset(self):
        return Purchase.objects.filter(store=get_current_store(self.request))

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        store = get_current_store(self.request)
        form.fields["supplier"].queryset = Supplier.objects.filter(store=store)
        return form


# =========================
# PURCHASE ITEM VIEWS
# =========================

class PurchaseItemListView(StoreRequiredMixin, ListView):
    model = PurchaseItem
    template_name = "inventory/purchases/purchase_item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        store = get_current_store(self.request)
        purchase_id = self.request.GET.get('purchase_id')

        if purchase_id:
            return PurchaseItem.objects.filter(
                purchase_id=purchase_id,
                purchase__store=store
            )

        return PurchaseItem.objects.filter(purchase__store=store)


class PurchaseItemCreateView(StoreRequiredMixin, CreateView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = "inventory/purchases/purchase_item_form.html"
    success_url = reverse_lazy("purchase_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        store = get_current_store(self.request)

        form.fields["purchase"].queryset = Purchase.objects.filter(store=store)
        form.fields["variant"].queryset = ProductVariant.objects.filter(
            product__store=store
        )

        purchase_id = self.request.GET.get("purchase_id")
        if purchase_id:
            form.initial["purchase"] = purchase_id
            form.fields["purchase"].disabled = True

        return form


class PurchaseItemUpdateView(StoreRequiredMixin, UpdateView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = "inventory/purchases/purchase_item_form.html"
    success_url = reverse_lazy("purchase_list")

    def get_queryset(self):
        return PurchaseItem.objects.filter(purchase__store=get_current_store(self.request))

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        store = get_current_store(self.request)

        form.fields["purchase"].queryset = Purchase.objects.filter(store=store)
        form.fields["variant"].queryset = ProductVariant.objects.filter(
            product__store=store
        )

        return form


class PurchaseItemDeleteView(StoreRequiredMixin, DeleteView):
    model = PurchaseItem
    template_name = "inventory/purchases/purchase_item_confirm_delete.html"
    success_url = reverse_lazy("purchase_list")

    def get_queryset(self):
        return PurchaseItem.objects.filter(purchase__store=get_current_store(self.request))