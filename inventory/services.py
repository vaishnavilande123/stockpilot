from .models import Inventory, Purchase, PurchaseItem, SaleItem, Product
from django.db.models import F, Q, Avg, Count, Sum
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncWeek


# ===========================
# INVENTORY ANALYTICS
# ===========================

def get_low_stock_items(store_id):
    return Inventory.objects.filter(
        store_id=store_id,
        quantity_available__lte=F("minimum_stock_level")
    ).select_related("variant", "variant__product")


def get_out_of_stock_items(store_id):
    return Inventory.objects.filter(
        store_id=store_id,
        quantity_available=0
    )


def get_dead_stock(store_id, days=30):
    threshold = timezone.now() - timedelta(days=days)

    return Inventory.objects.filter(
        store_id=store_id
    ).filter(
        Q(last_sale_date__lt=threshold) |
        Q(last_sale_date__isnull=True, last_updated__lt=threshold)
    )


# ===========================
# SALES ANALYTICS
# ===========================

def get_fast_moving_products(store_id, limit=5):
    return (
        SaleItem.objects
        .filter(sale__store_id=store_id)
        .values('variant__product', 'variant__product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:limit]
    )


def get_slow_moving_products(store_id, limit=5):
    return (
        SaleItem.objects
        .filter(sale__store_id=store_id)
        .values('variant__product', 'variant__product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('total_sold')[:limit]
    )


def get_sales_trend(store_id, days=7):
    start_date = timezone.now().date() - timedelta(days=days)
    return (
        SaleItem.objects
        .filter(sale__store_id=store_id, sale__sale_date__gte=start_date)
        .values('sale__sale_date')
        .annotate(
            total_revenue=Sum(F("selling_price") * F("quantity")),
            total_profit=Sum((F("selling_price") - F("cost_price")) * F("quantity"))
        )
        .order_by('sale__sale_date')
    )


# ===========================
# PROFIT ANALYTICS
# ===========================

def get_most_profitable_products(store_id, limit=5):
    return (
        SaleItem.objects
        .filter(sale__store_id=store_id)
        .values('variant__product', 'variant__product__name')
        .annotate(
            total_profit=Sum(
                (F("selling_price") - F("cost_price")) * F("quantity")
            )
        )
        .order_by('-total_profit')[:limit]
    )


# ===========================
# DEMAND ANALYTICS
# ===========================


def get_variant_average_weekly_demand(variant_id, store_id, weeks=8):
    start_date = timezone.now().date() - timedelta(weeks=weeks)

    data = (
        SaleItem.objects
        .filter(
            variant_id=variant_id,
            sale__store_id=store_id,
            sale__sale_date__gte=start_date
        )
        .annotate(week=TruncWeek("sale__sale_date"))
        .values("week")
        .annotate(total_sold=Sum("quantity"))
    )

    total_units = sum([row["total_sold"] for row in data])
    week_count = len(data)

    if week_count == 0:
        return 0

    return round(total_units / week_count, 2)


# ===========================
# SMART REORDER
# ===========================

def get_smart_reorder_alerts(store_id, weeks_threshold=2):

    inventory_items = Inventory.objects.filter(
        store_id=store_id
    ).select_related("variant", "variant__product")

    alerts = []

    for item in inventory_items:

        avg_demand = get_variant_average_weekly_demand(
            item.variant.id, store_id
        )

        if avg_demand == 0:
            continue

        weeks_left = item.quantity_available / avg_demand

        if weeks_left <= weeks_threshold:

            supplier_data = get_supplier_scores_for_product(
                item.variant.product.id, store_id
            )

            alerts.append({
                "product": item.variant.product.name,
                "variant": item.variant,
                "stock_left": item.quantity_available,
                "avg_weekly_sales": round(avg_demand, 2),
                "weeks_left": round(weeks_left, 2),
                "recommended_supplier": supplier_data["recommended_supplier"],
                "all_suppliers": supplier_data["suppliers"]
            })

    return alerts


# ===========================
# SUPPLIER ANALYTICS
# ===========================

def get_supplier_scores_for_product(product_id, store_id):

    purchases = Purchase.objects.filter(
        store_id=store_id,
        purchaseitem__variant__product_id=product_id
    ).values(
        'supplier',
        'supplier__supplier_name'
    ).annotate(
        total_orders=Count('id', distinct=True),
        delivered_orders=Count('id', filter=Q(order_status="Delivered"), distinct=True),
        cancelled_orders=Count('id', filter=Q(order_status="Cancelled"), distinct=True),
        on_time_deliveries=Count(
            'id',
            filter=Q(order_status="Delivered") &
                   Q(delivery_date__lte=F("expected_delivery_date")),
            distinct=True
        )
    )

    purchase_items = PurchaseItem.objects.filter(
        purchase__store_id=store_id,
        variant__product_id=product_id
    ).values('purchase__supplier').annotate(
        avg_discount=Avg('discount_percent'),
        total_delivered=Sum("delivered_quantity"),
        total_ordered=Sum("ordered_quantity")
    )

    item_map = {p['purchase__supplier']: p for p in purchase_items}

    results = []

    for row in purchases:

        supplier_id = row['supplier']
        supplier_name = row['supplier__supplier_name']

        total_orders = row['total_orders'] or 0
        delivered_orders = row['delivered_orders'] or 0
        cancelled_orders = row['cancelled_orders'] or 0
        on_time_deliveries = row['on_time_deliveries'] or 0

        item = item_map.get(supplier_id, {})

        avg_discount = item.get('avg_discount', 0) or 0
        total_delivered = item.get('total_delivered', 0) or 0
        total_ordered = item.get('total_ordered', 0) or 0

        delivery_success = (delivered_orders / total_orders * 100) if total_orders else 0
        cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders else 0
        on_time_rate = (on_time_deliveries / delivered_orders * 100) if delivered_orders else 0
        delivery_accuracy = (total_delivered / total_ordered * 100) if total_ordered else 0

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

    results = sorted(results, key=lambda x: x["reliability_score"], reverse=True)

    return {
        "suppliers": results,
        "recommended_supplier": results[0] if results else None
    }


# ===========================
# MULTI-STORE INSIGHTS 🔥
# ===========================

def get_store_profit():
    return (
        SaleItem.objects
        .values('sale__store__store_name')
        .annotate(
            total_profit=Sum(
                (F("selling_price") - F("cost_price")) * F("quantity")
            )
        )
        .order_by('-total_profit')
    )


def get_top_store():
    return (
        SaleItem.objects
        .values('sale__store__store_name')
        .annotate(
            total_profit=Sum(
                (F("selling_price") - F("cost_price")) * F("quantity")
            )
        )
        .order_by('-total_profit')
        .first()
    )


def get_best_store_this_week():
    start_date = timezone.now().date() - timedelta(days=7)

    return (
        SaleItem.objects
        .filter(sale__sale_date__gte=start_date)
        .values('sale__store__store_name')
        .annotate(
            total_profit=Sum(
                (F("selling_price") - F("cost_price")) * F("quantity")
            )
        )
        .order_by('-total_profit')
        .first()
    )