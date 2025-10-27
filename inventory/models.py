from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Medicine(models.Model):
    """
    Represents a product (medicine).
    total_stock is computed from related Batches (recommended) but we keep a denormalized field for fast queries.
    """
    sku = models.CharField(max_length=64, unique=True)  # stock keeping unit
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="medicines")
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_stock = models.IntegerField(default=0)  # denormalized (sum of available in batches)
    reorder_level = models.IntegerField(default=10, validators=[MinValueValidator(0)])  # threshold
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Batch(models.Model):
    """
    Represents a procurement batch for a Medicine, with expiry and quantity.
    """
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="batches")
    batch_number = models.CharField(max_length=128, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    available_quantity = models.IntegerField(validators=[MinValueValidator(0)])  # changes with sales/consumption
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="batches")
    received_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-received_date",)

    def __str__(self):
        return f"{self.medicine.name} - Batch {self.batch_number or self.pk}"

class PurchaseOrder(models.Model):
    """
    A PO from a supplier (incoming stock). status tracks workflow.
    """
    STATUS_DRAFT = "draft"
    STATUS_RECEIVED = "received"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_RECEIVED, "Received"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="purchase_orders")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="purchase_orders")
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"PO#{self.pk} - {self.supplier or 'Unknown'} - {self.status}"

    @property
    def total_cost(self):
        return sum(item.total_price for item in self.items.all())

class PurchaseItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    batch_number = models.CharField(max_length=128, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("purchase_order",)

    @property
    def total_price(self):
        return self.quantity * self.purchase_price

class StockTransaction(models.Model):
    """
    Tracks stock in/out movements for audit.
    type: 'in' for add stock, 'out' for consume/sell, 'adjust' for corrections.
    Related batch when applicable.
    """
    TYPE_IN = "in"
    TYPE_OUT = "out"
    TYPE_ADJUST = "adjust"
    TYPE_CHOICES = [
        (TYPE_IN, "In"),
        (TYPE_OUT, "Out"),
        (TYPE_ADJUST, "Adjust"),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="transactions")
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.IntegerField()  # positive integer; sign is by transaction_type
    note = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="stock_transactions")
    performed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-performed_at",)


