from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from ..models import Inventory, Store
from .landing_views import StoreRequiredMixin

# =========================
# HELPER FUNCTION
# =========================
def get_current_store(request):
    store_id = request.session.get("store_id")
    return get_object_or_404(Store, id=store_id)


# =========================
# INVENTORY LIST VIEW
# =========================
class InventoryListView(StoreRequiredMixin,ListView):
    model = Inventory
    template_name = "inventory/inventories/inventory_list.html"
    context_object_name = "stocks"

    def get_queryset(self):
        store = get_current_store(self.request)
        return Inventory.objects.filter(store=store).select_related(
            "variant",
            "variant__product"
        )