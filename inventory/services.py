from .models import Inventory, Purchase, PurchaseItem, SaleItem, Product, Supplier
from django.db.models import F, Q, Avg, Count, Sum

def get_low_stock_items():
  return Inventory.objects.filter(
    quantity_available__lte=F("minimum_stock_level")
  )

def get_fast_moving_products(limit=5):
  return(
    SaleItem.objects
    .values('variant__product', 'variant__product__name')
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


  #optimized one check later on
  # Product.objects.annotate(
  #   profit=F("selling_price") - F("cost_price")
  # ).order_by("-profit")[:limit]


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
    total_orders = s['total_orders'] or 0
    delivered_orders = s['delivered_orders'] or 0
    cancelled_orders = s['cancelled_orders'] or 0
    on_time_deliveries = s['on_time_deliveries'] or 0

    item_data = discount_map.get(supplier_id)

    if item_data:
      avg_discount = item_data['avg_discount'] or 0
      total_delivered = item_data["total_delivered"] or 0
      total_ordered = item_data["total_ordered"] or 0
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
  

def get_supplier_scores_for_product(product_id):
  data = PurchaseItem.objects.filter(variant__product_id = product_id
  ).values(
    "purchase__supplier", "purchase__supplier__supplier_name"
  ).annotate(
    total_ordered = Sum("ordered_quantity"),
    total_delivered = Sum("delivered_quantity"),
    avg_discount = Avg('discount_percent'),

    total_orders=Count('purchase', distinct=True),

    delivered_orders=Count("purchase", filter=Q(purchase__order_status="Delivered"), distinct=True),

    cancelled_orders=Count('purchase', filter=Q(purchase__order_status="Cancelled"), distinct = True), 

    on_time_deliveries=Count("purchase", filter = Q (purchase__order_status="Delivered") & Q(purchase__delivery_date__lte = F("purchase__expected_delivery_date")), distinct = True)

  )

  results = []

  for row in data:

    supplier_id = row["purchase__supplier"]
    supplier_name = row["purchase__supplier__supplier_name"]

    total_orders = row["total_orders"] or 0
    delivered_orders = row["delivered_orders"] or 0
    cancelled_orders = row["cancelled_orders"] or 0
    on_time_deliveries = row["on_time_deliveries"] or 0

    total_ordered = row["total_ordered"] or 0
    total_delivered = row["total_delivered"] or 0

    avg_discount = row["avg_discount"] or 0


    # ---------- calculate metrics ----------

    if total_orders > 0:
        delivery_success = (delivered_orders / total_orders) * 100
        cancellation_rate = (cancelled_orders / total_orders) * 100
    else:
        delivery_success = 0
        cancellation_rate = 0

    if delivered_orders > 0:
        on_time_rate = (on_time_deliveries / delivered_orders) * 100
    else:
        on_time_rate = 0

    if total_ordered > 0:
        delivery_accuracy = (total_delivered / total_ordered) * 100
    else:
        delivery_accuracy = 0


    # ---------- reliability score ----------

    reliability_score = (
        delivery_success +
        on_time_rate +
        (100 - cancellation_rate) +
        delivery_accuracy +
        avg_discount
    ) / 5


    results.append({
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "delivery_success": round(delivery_success, 2),
        "on_time_rate": round(on_time_rate, 2),
        "cancellation_rate": round(cancellation_rate, 2),
        "delivery_accuracy": round(delivery_accuracy, 2),
        "avg_discount": round(avg_discount, 2),
        "reliability_score": round(reliability_score, 2)
    })


  # sort suppliers by reliability score
  results = sorted(results, key=lambda x: x["reliability_score"], reverse=True)


  best_supplier = results[0] if results else None

  return {
      "suppliers": results,
      "recommended_supplier": best_supplier
  }




