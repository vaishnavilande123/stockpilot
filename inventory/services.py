from .models import Inventory, SaleItem, Product
from django.db.models import F, Sum

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