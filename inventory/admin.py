from django.contrib import admin
from .models import Store, Category, Product, ProductVariant, Inventory, Supplier, Purchase, PurchaseItem, Sale, SaleItem

admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Inventory)
admin.site.register(Supplier)
admin.site.register(Purchase)
admin.site.register(PurchaseItem)
admin.site.register(Sale)
admin.site.register(SaleItem)

