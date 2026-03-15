from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import Sale
from ..forms.sale_forms import SaleForm
from ..models import SaleItem
from ..forms.sale_forms import SaleItemForm


class SaleListView(ListView):
    model = Sale
    template_name = "inventory/sales/sale_list.html"
    context_object_name = "sales"


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "inventory/sales/sale_form.html"
    success_url = reverse_lazy("sale_list")


class SaleUpdateView(UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = "inventory/sales/sale_form.html"
    success_url = reverse_lazy("sale_list")


class SaleDeleteView(DeleteView):
    model = Sale
    template_name = "inventory/sales/sale_confirm_delete.html"
    success_url = reverse_lazy("sale_list")


class SaleItemListView(ListView):
    model = SaleItem
    template_name = "inventory/sales/sale_item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        sale_id = self.request.GET.get("sale_id")

        if sale_id:
            return SaleItem.objects.filter(sale_id=sale_id)

        return SaleItem.objects.all()
    

class SaleItemCreateView(CreateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = "inventory/sales/sale_item_form.html"
    success_url = reverse_lazy("sale_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        sale_id = self.request.GET.get("sale_id")

        if sale_id:
            form.initial["sale"] = sale_id
            form.fields["sale"].disabled = True

        return form

class SaleItemUpdateView(UpdateView):
    model = SaleItem
    form_class = SaleItemForm
    template_name = "inventory/sales/sale_item_form.html"
    success_url = reverse_lazy("sale_list")


class SaleItemDeleteView(DeleteView):
    model = SaleItem
    template_name = "inventory/sales/sale_item_confirm_delete.html"
    success_url = reverse_lazy("sale_list")
    
                