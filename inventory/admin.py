from django.contrib import admin
from .models import Category, Supplier, Medicine, Batch, PurchaseOrder, PurchaseItem, StockTransaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone")

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "total_stock", "reorder_level", "is_active")
    search_fields = ("name", "sku")

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("medicine", "batch_number", "available_quantity", "expiry_date", "received_date")

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "status", "created_by", "created_at")
    inlines = [PurchaseItemInline]

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ("medicine", "transaction_type", "quantity", "performed_by", "performed_at")
