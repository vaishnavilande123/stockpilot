from django.views.generic import TemplateView
import json
from decimal import Decimal
from datetime import date

from ..models import Product, ProductVariant, Supplier
from .landing_views import StoreRequiredMixin
from ..services import (
    get_low_stock_items,
    get_out_of_stock_items,
    get_dead_stock,
    get_fast_moving_products,
    get_slow_moving_products,
    get_sales_trend,
    get_most_profitable_products,
    get_smart_reorder_alerts,
    get_store_profit,
    get_top_store,
    get_best_store_this_week
)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError

class DashboardView(StoreRequiredMixin,TemplateView):

    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # =========================
        # STORE SESSION
        # =========================
        store_id = self.request.session.get("store_id")

        # If no store selected
        if not store_id:
            context["error"] = "No store selected"
            return context

        # =========================
        # FILTERED QUERYSETS
        # =========================
        products = Product.objects.filter(store_id=store_id)
        variants = ProductVariant.objects.filter(product__store_id=store_id)
        suppliers = Supplier.objects.filter(store_id=store_id)

        # =========================
        # 1. SUMMARY COUNTS (STORE BASED)
        # =========================
        context["total_products"] = products.count()
        context["total_variants"] = variants.count()
        context["total_suppliers"] = suppliers.count()

        # =========================
        # 2. INVENTORY ALERTS (STORE BASED)
        # =========================
        context["low_stock_items"] = get_low_stock_items(store_id)
        context["out_of_stock_items"] = get_out_of_stock_items(store_id)
        context["dead_stock_items"] = get_dead_stock(store_id)

        context["low_stock_count"] = context["low_stock_items"].count()
        context["out_of_stock_count"] = context["out_of_stock_items"].count()
        context["dead_stock_count"] = context["dead_stock_items"].count()

        healthy_stock = context["total_variants"] - context["low_stock_count"] - context["out_of_stock_count"]
        
        # Prepare JSON for Inventory Chart
        context["chart_inventory"] = json.dumps({
            "labels": ["Healthy", "Low Stock", "Out of Stock"],
            "data": [healthy_stock, context["low_stock_count"], context["out_of_stock_count"]]
        })

        # =========================
        # 3. SALES INSIGHTS (STORE BASED)
        # =========================
        fast_moving = get_fast_moving_products(store_id)
        context["fast_moving_products"] = fast_moving
        context["slow_moving_products"] = get_slow_moving_products(store_id)

        # Prepare JSON for Fast Moving Chart
        context["chart_fast_moving"] = json.dumps({
            "labels": [item['variant__product__name'] for item in fast_moving],
            "data": [item['total_sold'] for item in fast_moving]
        }, default=decimal_default)

        # =========================
        # 4. PROFIT INSIGHTS (STORE BASED)
        # =========================
        profitable = get_most_profitable_products(store_id)
        context["profitable_products"] = profitable

        # Prepare JSON for Profitable Products Chart
        context["chart_profitable"] = json.dumps({
            "labels": [item['variant__product__name'] for item in profitable],
            "data": [item['total_profit'] for item in profitable]
        }, default=decimal_default)

        # =========================
        # 4.5 SALES TREND (STORE BASED)
        # =========================
        trend = get_sales_trend(store_id, days=7)
        context["chart_sales_trend"] = json.dumps({
            "labels": [item['sale__sale_date'] for item in trend],
            "revenue": [item['total_revenue'] for item in trend],
            "profit": [item['total_profit'] for item in trend]
        }, default=decimal_default)

        # =========================
        # 5. SMART REORDER (STORE BASED)
        # =========================
        context["reorder_alerts"] = get_smart_reorder_alerts(store_id)
        context["reorder_count"] = len(context["reorder_alerts"])

        # =========================
        # 6. MULTI-STORE ANALYTICS
        # =========================
        store_profits = get_store_profit()
        context["store_profits"] = store_profits  # all stores
        context["top_store"] = get_top_store()         # best overall
        context["best_store_week"] = get_best_store_this_week()

        # Prepare JSON for Multi-Store Chart
        context["chart_store_profits"] = json.dumps({
            "labels": [item['sale__store__store_name'] for item in store_profits],
            "data": [item['total_profit'] for item in store_profits]
        }, default=decimal_default)

        return context