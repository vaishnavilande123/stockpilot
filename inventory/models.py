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
  
  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=["product", "size", "color"],
        name="unique_product_variant"
      )
    ]
  

class Inventory(models.Model):
  variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE)
  store = models.ForeignKey(Store, on_delete=models.CASCADE)

  quantity_available = models.IntegerField(default=0)
  minimun_stock_level = models.IntegerField(default=5)
  last_updated = models.DateTimeField(auto_now=True)
  last_sale_date = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return f"{self.variant} - Stock: {self.quantity_available}"
  
  @property
  def needs_reorder(self):
    return self.quantity_available <= self.minimun_stock_level


class Supplier(models.Model):
  store = models.ForeignKey(Store, on_delete=models.CASCADE)
  supplier_name = models.CharField(max_length=200)

  phone = models.CharField(max_length=15)
  email = models.EmailField(blank=True, null=True)
  city = models.CharField(max_length=100)
  address = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add = True)

  def __str__(self):
    return self.supplier_name
  

class Purchase(models.Model):

  STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
    ('Partially Delivered', 'Partially Delivered'),
  ]  

  store = models.ForeignKey(Store, on_delete=models.CASCADE)
  supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

  order_date = models.DateField()
  expected_delivery_date = models.DateField()
  delivery_date = models.DateField(null=True, blank=True)

  order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')

  total_cost = models.DecimalField(max_digits=15, decimal_places=2)

  def __str__(self):
    return f"Purchase{self.id} - {self.supplier.supplier_name}"


class PurchaseItem(models.Model):
  purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
  variant = models.ForeignKey(ProductVariant, 
  on_delete=models.CASCADE)

  ordered_quantity = models.IntegerField()
  delivered_quantity = models.IntegerField(default=0)

  unit_cost = models.DecimalField(max_digits=10, decimal_places = 2)

  discount_percent = models.FloatField(default=0)

  def __str__(self):
    return f"{self.variant} - {self.ordered_quantity}"
  
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    inventory, created = Inventory.objects.get_or_create(
      variant = self.variant,
      store = self.purchase.store
    )

    inventory.quantity_available += self.delivered_quantity
    inventory.save()



class Sale(models.Model):
  store = models.ForeignKey(Store, on_delete=models.CASCADE)
  sale_date = models.DateField()
  total_amount = models.DecimalField(max_digits=15, decimal_places=2)

  def __str__(self):
    return f"Sale{self.id} - {self.sale_date}"
  

class SaleItem(models.Model):
  sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
  variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

  quantity = models.IntegerField()
  selling_price = models.DecimalField(max_digits=10, decimal_places=2)

  def __str__(self):
    return f"{self.variant} - {self.quantity}"
  
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    try:
      inventory = Inventory.objects.get(
        variant=self.variant,
        store=self.sale.store
      )

      inventory.quantity_available -= self.quantity
      inventory.last_sale_date = self.sale.sale_date
      inventory.save()

    except Inventory.DoesNotExist:
      pass  
    




