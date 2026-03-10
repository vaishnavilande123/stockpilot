from .models import Inventory, Purchase, PurchaseItem, SaleItem, Product, Supplier
from django.db.models import F, Q, Avg, Count, Sum

def get_low_stock_items():
  return Inventory.objects.filter(
    quantity_available__lte=F("minimum_stock_level")
  )

def get_fast_moving_products(limit=5):
  return(
    SaleItem.objects
    .values('variant__product')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')[:limit]
  )

def get_most_profitable_products(limit=5):
  products = Product.objects.all()

  product_profits = []

  for product in products:
    profit = product.selling_price - product.cost_price
    product_profits.append({
      "product" : product.name,
      "profit_per_unit": profit
    })

  product_profits.sort(key=lambda x: x["profit_per_unit"], reverse=True)

  return product_profits[:limit]  


def get_supplier_reliability():
  supplier = Purchase.objects.values('supplier', 'supplier__supplier_name').annotate(
    total_orders=Count('id'),
    delivered_orders=Count("id", filter=Q(order_status="Delivered")),
    cancelled_orders=Count('id', filter=Q(order_status="Cancelled")), 
    on_time_deliveries=Count("id", filter = Q(order_status="Delivered") & Q(delivery_date__lte = F("expected_delivery_date")))
  )
  
  purchase_data = PurchaseItem.objects.values('purchase__supplier').annotate(
    avg_discount = Avg('discount_percent'),
    total_delivered=Sum("ordered_qunatity"),
    total_ordered=Sum("ordered_qunatity")
  )
  
