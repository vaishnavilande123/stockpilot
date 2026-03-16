from .models import Inventory, Purchase, PurchaseItem, SaleItem, Product, Supplier
from django.db.models import F, Q, Avg, Count, Sum
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncWeek

#---------------------------Inventory analytics-----------------------------
def get_low_stock_items():
  return Inventory.objects.filter(
    quantity_available__lte=F("minimum_stock_level")
  ).select_related("variant", "variant__product")

def get_out_of_stock_items():
    return Inventory.objects.filter(quantity_available=0)

def get_dead_stock(days=30):
    threshold = timezone.now().date() - timedelta(days=days)

    return Inventory.objects.filter(
    Q(last_sale_date__lt=threshold) | Q(last_sale_date__isnull=True)
    )

#--------------------------Sales analytics-----------------------
def get_fast_moving_products(limit=5):
  return(
    SaleItem.objects
    .values('variant__product', 'variant__product__name')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')[:limit]
  )

def get_slow_moving_products(limit=5):
    return (
        SaleItem.objects
        .values('variant__product', 'variant__product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('total_sold')[:limit]
    )

#-------------------Profit analytics-----------------------
def get_most_profitable_products(limit=5):

    return (
        SaleItem.objects
        .values('variant__product', 'variant__product__name')
        .annotate(
            total_profit=Sum(
                (F("selling_price") - F("variant__product__cost_price")) * F("quantity")
            )
        )
        .order_by('-total_profit')[:limit]
    )

#-------------------Demand analytics-----------------------
def get_product_weekly_demand(product_id, weeks=8):

    start_date = timezone.now().date() - timedelta(weeks=weeks)

    data = (
        SaleItem.objects
        .filter(
            variant__product_id=product_id,
            sale__sale_date__gte=start_date
        )
        .annotate(week=TruncWeek("sale__sale_date"))
        .values("week")
        .annotate(total_sold=Sum("quantity"))
        .order_by("week")
    )

    return data

def get_average_weekly_demand(product_id, weeks=8):

    weekly_data = get_product_weekly_demand(product_id, weeks)

    total_units = 0
    week_count = 0

    for row in weekly_data:
        total_units += row["total_sold"]
        week_count += 1

    if week_count == 0:
        return 0

    avg_demand = total_units / week_count

    return round(avg_demand, 2)


#-------------------Supplier analytics-----------------------
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




