from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from django.utils import timezone


# ===========================
# STORE
# ===========================

class Store(models.Model):
    store_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'store_name', 'location'],
                name='unique_store_per_owner_location'
            )
        ]


# ===========================
# CATEGORY
# ===========================

class Category(models.Model):
    name = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.store.store_name})"


# ===========================
# PRODUCT
# ===========================

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    marked_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    barcode = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.store.store_name})"

    def clean(self):
        if self.store_id and self.category_id:
            if self.category.store_id != self.store_id:
                raise ValidationError("Category and Product must belong to same store")


# ===========================
# PRODUCT VARIANT
# ===========================

class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    sku = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                name="unique_product_variant"
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.name[:3].upper()}-{self.size}-{self.color[:3].upper()}"
        super().save(*args, **kwargs)


# ===========================
# INVENTORY
# ===========================

class Inventory(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    quantity_available = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minimum_stock_level = models.IntegerField(default=5, validators=[MinValueValidator(0)])

    last_updated = models.DateTimeField(auto_now=True)
    last_sale_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['variant', 'store']

    def __str__(self):
        return f"{self.variant} ({self.store.store_name}) - {self.quantity_available}"

    @property
    def needs_reorder(self):
        return self.quantity_available <= self.minimum_stock_level


# ===========================
# SUPPLIER
# ===========================

class Supplier(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=200)

    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^[6-9]\d{9}$', "Enter valid 10-digit phone number")]
    )

    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.supplier_name} ({self.store.store_name})"


# ===========================
# PURCHASE
# ===========================

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)

    order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')

    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    def update_total_cost(self):
        total = sum([
            item.delivered_quantity * item.unit_cost * (1 - Decimal(item.discount_percent) / 100)
            for item in self.purchaseitem_set.all()
        ])
        self.total_cost = total
        self.save(update_fields=["total_cost"])

    def delete(self, *args, **kwargs):

        # If purchase was delivered → reverse inventory
        if self.order_status == "Delivered":

            for item in self.purchaseitem_set.all():

                try:
                    inventory = Inventory.objects.get(
                        variant=item.variant,
                        store=self.store
                    )

                    inventory.quantity_available -= item.delivered_quantity
                    inventory.save()

                except Inventory.DoesNotExist:
                    pass

        super().delete(*args, **kwargs)    


# ===========================
# PURCHASE ITEM
# ===========================

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    ordered_quantity = models.IntegerField(validators=[MinValueValidator(1)])
    delivered_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_percent = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def clean(self):
        if self.discount_percent > 100:
            raise ValidationError("Discount cannot exceed 100%")
        if self.delivered_quantity > self.ordered_quantity:
            raise ValidationError("Delivered cannot exceed ordered")

    def save(self, *args, **kwargs):
        if self.pk:
            old = PurchaseItem.objects.get(pk=self.pk)
            old_qty = old.delivered_quantity
        else:
            old_qty = 0

        super().save(*args, **kwargs)

        if self.purchase.order_status == "Delivered":
            inventory, _ = Inventory.objects.get_or_create(
                variant=self.variant,
                store=self.purchase.store
            )
            inventory.quantity_available += (self.delivered_quantity - old_qty)
            inventory.save()

        self.purchase.update_total_cost()

    def delete(self, *args, **kwargs):
        if self.purchase.order_status == "Delivered":
            inventory = Inventory.objects.get(
                variant=self.variant,
                store=self.purchase.store
            )
            inventory.quantity_available -= self.delivered_quantity
            inventory.save()

        super().delete(*args, **kwargs)
        self.purchase.update_total_cost()


# ===========================
# SALE
# ===========================

class Sale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    sale_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    def update_total_amount(self):
        total = sum([
            item.quantity * item.selling_price
            for item in self.saleitem_set.all()
        ])
        self.total_amount = total
        self.save(update_fields=["total_amount"])


# ===========================
# SALE ITEM
# ===========================

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # NEW FIELD → store actual cost at time of sale
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )

    def __str__(self):
        return f"{self.variant} - {self.quantity}"

    def clean(self):
        super().clean()
        # Ensure related required fields are present before checking
        if not self.sale_id or not self.variant_id or self.quantity is None:
            return

        if self.pk:
            old = SaleItem.objects.get(pk=self.pk)
            old_qty = old.quantity
        else:
            old_qty = 0

        inventory = Inventory.objects.filter(
            variant_id=self.variant_id,
            store_id=self.sale.store_id
        ).first()

        quantity_available = inventory.quantity_available if inventory else 0
        diff = self.quantity - old_qty

        if quantity_available < diff:
            raise ValidationError("Not enough stock")

        purchase_item = PurchaseItem.objects.filter(
            variant_id=self.variant_id,
            purchase__store_id=self.sale.store_id,
            purchase__order_status="Delivered"
        ).order_by('-id').first()

        if not purchase_item:
            raise ValidationError("No purchase record found for this product")

    def save(self, *args, **kwargs):

        # =========================
        # OLD QUANTITY (for update)
        # =========================
        if self.pk:
            old = SaleItem.objects.get(pk=self.pk)
            old_qty = old.quantity
        else:
            old_qty = 0

        # =========================
        # GET INVENTORY
        # =========================
        inventory, _ = Inventory.objects.get_or_create(
            variant=self.variant,
            store=self.sale.store
        )

        diff = self.quantity - old_qty

        # =========================
        # 🔥 REAL COST FROM PURCHASE
        # =========================
        purchase_item = PurchaseItem.objects.filter(
            variant=self.variant,
            purchase__store=self.sale.store,
            purchase__order_status="Delivered"
        ).order_by('-id').first()

        if purchase_item:
            discount = Decimal(purchase_item.discount_percent) / Decimal(100)
            actual_cost = purchase_item.unit_cost * (Decimal(1) - discount)
            self.cost_price = actual_cost

        # =========================
        # SAVE SALE ITEM
        # =========================
        super().save(*args, **kwargs)

        # =========================
        # UPDATE INVENTORY
        # =========================
        inventory.quantity_available -= diff
        inventory.last_sale_date = self.sale.sale_date
        inventory.save()

        # =========================
        # UPDATE TOTAL SALE
        # =========================
        self.sale.update_total_amount()

    def delete(self, *args, **kwargs):

        inventory = Inventory.objects.get(
            variant=self.variant,
            store=self.sale.store
        )

        inventory.quantity_available += self.quantity
        inventory.save()

        super().delete(*args, **kwargs)

        self.sale.update_total_amount()