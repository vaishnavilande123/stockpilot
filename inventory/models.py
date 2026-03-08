from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
  store_name = models.CharField(max_length = 200)
  location = models.CharField(max_length=200)
  owner = models.ForeignKey(User, on_delete = models.CASCADE)
  created_at = models.DateTimeField(auto_now_add = True)

  def __str__(self):
    return self.store_name
  
class Category(models.Model):
  name = models.CharField(max_length=100)
  store = models.ForeignKey(Store, on_delete = models.CASCADE)

  def __str__(self):
    return self.name
  

class Product(models.Model):
  name = models.CharField(max_length=200)
  category = models.ForeignKey(Category, on_delete = models.CASCADE)
  store = models.ForeignKey(Store, on_delete = models.CASCADE)
  cost_price = models.DecimalField(max_digits = 10, decimal_places=2)
  selling_price = models.DecimalField(max_digits=10, decimal_places=2)
  barcode = models.CharField(max_length=100, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
   
  def __str__(self):
    return self.name


class ProductVariant(models.Model):
  product = models.ForeignKey(Product, on_delete = models.CASCADE)
  size = models.CharField(max_length=20)
  color = models.CharField(max_length=50)
  #stock keeping unit
  sku = models.CharField(max_length=100, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.product.name} - {self.size} - {self.color}"
  

class Inventory(models.Model):
  variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE)
  store = models.ForeignKey(Store, on_delete=models.CASCADE)
  quantity_available = models.IntegerField(default=0)
  minimun_stock_level = models.IntegerField(default=5)
  last_updated = models.DateTimeField(auto_now=True)
  last_sale_date = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return f"{self.variant} - Stock: {self.quantity_available}"
  
    
