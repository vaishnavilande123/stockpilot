from django.db import IntegrityError

from django.shortcuts import render, redirect, get_object_or_404
from ..models import Store
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from ..models import Store
from ..forms.store_forms import StoreForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


# =========================
# STORE LIST + SELECT PAGE
# =========================
class StoreListView(LoginRequiredMixin, ListView):
    model = Store
    template_name = "inventory/stores/store.html"
    context_object_name = "stores"

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)


# =========================
# CREATE STORE
# =========================
class StoreCreateView(LoginRequiredMixin, CreateView):
    model = Store
    form_class = StoreForm
    template_name = "inventory/stores/store_form.html"
    success_url = reverse_lazy('show_store')

     
    def form_valid(self, form):
        try:
            form.instance.owner = self.request.user
            response = super().form_valid(form)

            messages.success(self.request, "Store created successfully!")
            return response
        
        except IntegrityError:
            form.add_error(None, "Store with this name already exists at this location.")
            return self.form_invalid(form)

# =========================
# DELETE STORE
# =========================
class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    template_name = "inventory/stores/store_confirm_delete.html"
    success_url = reverse_lazy('show_store')

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Store deleted successfully!")
        return super().delete(request, *args, **kwargs)


def select_store(request):
    if request.user.is_superuser:
        return redirect("admin:index")

    if not request.user.is_authenticated:
        return redirect("login")

    stores = Store.objects.filter(owner=request.user)

    if request.method == "POST":
        store_id = request.POST.get("store_id")

        store = get_object_or_404(Store, id=store_id, owner=request.user)

        request.session["store_id"] = store.id
        request.session["store_name"] = store.store_name

        return redirect("dashboard")

    return render(request, "inventory/stores/store.html", {"stores": stores})