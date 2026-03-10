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
    total_delivered=Sum("delivered_quantity"),
    total_ordered=Sum("ordered_quantity")
  )
  
  discount_map = {}
  for p in purchase_data:
    supplier_id = p['purchase__supplier']
    discount_map[supplier_id] = p


  results = []
  for s in supplier:
    
    supplier_id = s['supplier']
    supplier_name = s['supplier__supplier_name']
    total_orders = s['total_orders']
    delivered_orders = s['delivered_orders']
    cancelled_orders = s['cancelled_orders']
    on_time_deliveries = s['on_time_deliveries']

    item_data = discount_map.get(supplier_id)

    if item_data:
      avg_discount = item_data['avg_disocunt']
      total_delivered = item_data["total_delivered"]
      total_ordered = item_data["total_ordered"]
    else:
      avg_discount = 0
      total_delivered = 0
      total_ordered = 0

    if total_orders > 0:
      delivery_success = (delivered_orders / total_orders)*100
      cancellation_rate = (cancelled_orders / total_orders)*100
    else:
      delivery_success=0
      cancellation_rate=0

    if delivered_orders > 0:
      on_time_rate = (on_time_deliveries / delivered_orders) * 100    
    else:
      on_time_rate = 0

    if total_ordered > 0:
      delivery_accuracy = (total_delivered/ total_ordered) * 100
    else:
      delivery_accuracy = 0      


    reliability_score = (
      delivery_success +
      on_time_rate +
      (100 - cancellation_rate) +
      delivery_accuracy +
      avg_discount
    ) /5

    results.append({
      "supplier_id": supplier_id,
      "supplier_name": supplier_name,
      "delivery_success": delivery_success,
      "on_time_rate": on_time_rate,
      "cancellation_rate": cancellation_rate,
      "delivery_accuracy": delivery_accuracy,
      "avg_discount": avg_discount,
      "reliability_score": reliability_score
    })

    results = sorted(results, key=lambda x: x['reliability_score'], reverse=True)
    
    return results