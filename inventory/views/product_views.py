from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from ..models import Product, Store, Category
from ..forms.product_forms import ProductForm
from ..services import get_supplier_scores_for_product
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
class ProductListView(StoreRequiredMixin, ListView):
    model = Product
    template_name = "inventory/products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        store = get_current_store(self.request)
        return Product.objects.filter(store=store)


# =========================
# CREATE VIEW
# =========================
class ProductCreateView(StoreRequiredMixin,CreateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/products/product_form.html"
    success_url = reverse_lazy("product_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # filter categories by store
        store = get_current_store(self.request)
        form.fields['category'].queryset = Category.objects.filter(store=store)

        return form

    def form_valid(self, form):
        form.instance.store_id  = self.request.session.get("store_id")
        return super().form_valid(form)


# =========================
# UPDATE VIEW
# =========================
class ProductUpdateView(StoreRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/products/product_form.html"
    success_url = reverse_lazy("product_list")

    def get_queryset(self):
        store = get_current_store(self.request)
        return Product.objects.filter(store=store)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        store = get_current_store(self.request)
        form.fields['category'].queryset = Category.objects.filter(store=store)

        return form


# =========================
# DELETE VIEW
# =========================
class ProductDeleteView(StoreRequiredMixin,DeleteView):
    model = Product
    template_name = "inventory/products/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")

    def get_queryset(self):
        store = get_current_store(self.request)
        return Product.objects.filter(store=store)
    


def product_suppliers_view(request, product_id):
    store = get_current_store(request)

    product = get_object_or_404(Product, id=product_id, store=store)

    supplier_data = get_supplier_scores_for_product(product.id, store)

    context = {
        "product": product,
        "suppliers": supplier_data["suppliers"],
        "recommended_supplier": supplier_data["recommended_supplier"]
    }

    return render(request, "inventory/products/product_suppliers.html", context)    