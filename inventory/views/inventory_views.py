from django.views.generic import ListView
from ..models import Inventory

class InventoryListView(ListView):
  model = Inventory
  template_name = "inventory/inventories/inventory_list.html"
  context_object_name = "stocks"

  