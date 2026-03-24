from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from ..models import ProductVariant, Product, Store
from ..forms.product_variant_forms import ProductVariantForm
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
class ProductVariantListView(StoreRequiredMixin,ListView):
    model = ProductVariant
    template_name = "inventory/product_variants/product_variant_list.html"
    context_object_name = 'product_variants'

    def get_queryset(self):
        store = get_current_store(self.request)

        product_id = self.request.GET.get("product_id")

        # If product selected → show only its variants
        if product_id:
            return ProductVariant.objects.filter(
                product_id=product_id,
                product__store=store
            )

        # Otherwise → show all variants of store
        return ProductVariant.objects.filter(product__store=store)


# =========================
# CREATE VIEW
# =========================
class ProductVariantCreateView(StoreRequiredMixin,CreateView):
    model = ProductVariant
    template_name = "inventory/product_variants/product_variant_form.html"
    form_class = ProductVariantForm
    success_url = reverse_lazy('product_variant_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        store = get_current_store(self.request)

        # Show only products of this store
        form.fields['product'].queryset = Product.objects.filter(store=store)

        # If coming from product → auto-select it
        product_id = self.request.GET.get('product_id')

        if product_id:
            form.initial['product'] = product_id
            form.fields['product'].disabled = True

        return form


# =========================
# UPDATE VIEW
# =========================
class ProductVariantUpdateView(StoreRequiredMixin,UpdateView):
    model = ProductVariant
    template_name = "inventory/product_variants/product_variant_form.html"
    form_class = ProductVariantForm
    success_url = reverse_lazy('product_variant_list')

    def get_queryset(self):
        store = get_current_store(self.request)
        return ProductVariant.objects.filter(product__store=store)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        store = get_current_store(self.request)
        form.fields['product'].queryset = Product.objects.filter(store=store)

        return form


# =========================
# DELETE VIEW
# =========================
class ProductVariantDeleteView(StoreRequiredMixin,DeleteView):
    model = ProductVariant
    template_name = "inventory/product_variants/product_variant_confirm_delete.html"
    success_url = reverse_lazy('product_variant_list')

    def get_queryset(self):
        store = get_current_store(self.request)
        return ProductVariant.objects.filter(product__store=store)