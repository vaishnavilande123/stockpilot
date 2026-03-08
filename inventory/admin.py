from django.contrib import admin
from .models import Store, Category, Product, ProductVariant, Inventory

admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Inventory)


