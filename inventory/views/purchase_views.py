from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import Purchase
from ..forms.purchase_forms import PurchaseForm


class PurchaseListView(ListView):
    model = Purchase
    template_name = "inventory/purchases/purchase_list.html"
    context_object_name = "purchases"


class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "inventory/purchases/purchase_form.html"
    success_url = reverse_lazy("purchase_list")


class PurchaseUpdateView(UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "inventory/purchases/purchase_form.html"
    success_url = reverse_lazy("purchase_list")


class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = "inventory/purchases/purchase_confirm_delete.html"
    success_url = reverse_lazy("purchase_list")


#__________________________PurchaseItem Views__________________________________

from ..models import PurchaseItem
from ..forms.purchase_forms import PurchaseItemForm


class PurchaseItemListView(ListView):
    model = PurchaseItem
    template_name = "inventory/purchases/purchase_item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        purchase_id = self.request.GET.get('purchase_id')

        if purchase_id:
            return PurchaseItem.objects.filter(purchase_id=purchase_id)

        return PurchaseItem.objects.all()


class PurchaseItemCreateView(CreateView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = "inventory/purchases/purchase_item_form.html"
    success_url = reverse_lazy("purchase_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        purchase_id = self.request.GET.get("purchase_id")

        if purchase_id:
            form.initial["purchase"] = purchase_id
            form.fields["purchase"].disabled = True

        return form


class PurchaseItemUpdateView(UpdateView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = "inventory/purchases/purchase_item_form.html"
    success_url = reverse_lazy("purchase_list")


class PurchaseItemDeleteView(DeleteView):
    model = PurchaseItem
    template_name = "inventory/purchases/purchase_item_confirm_delete.html"
    success_url = reverse_lazy("purchase_list")    