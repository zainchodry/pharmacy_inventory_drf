from rest_framework import serializers
from .models import Category, Supplier, Medicine, Batch, PurchaseOrder, PurchaseItem, StockTransaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description")

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name", "contact_email", "phone", "address", "notes")

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ("id", "batch_number", "quantity", "available_quantity", "purchase_price", "supplier", "received_date", "expiry_date", "created_at")
        read_only_fields = ("created_at",)

class MedicineSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category", write_only=True, required=False, allow_null=True)
    batches = BatchSerializer(many=True, read_only=True)

    class Meta:
        model = Medicine
        fields = ("id", "sku", "name", "category", "category_id", "description", "unit_price", "total_stock", "reorder_level", "is_active", "batches", "created_at")
        read_only_fields = ("total_stock", "created_at")

class PurchaseItemSerializer(serializers.ModelSerializer):
    medicine = serializers.PrimaryKeyRelatedField(queryset=Medicine.objects.all())
    medicine_detail = MedicineSerializer(source="medicine", read_only=True)

    class Meta:
        model = PurchaseItem
        fields = ("id", "medicine", "medicine_detail", "batch_number", "quantity", "purchase_price")

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    supplier_detail = SupplierSerializer(source="supplier", read_only=True)
    created_by = serializers.ReadOnlyField(source="created_by.email")
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ("id", "supplier", "supplier_detail", "created_by", "created_at", "status", "note", "items", "total_cost")
        read_only_fields = ("created_at", "created_by", "total_cost")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user
        po = PurchaseOrder.objects.create(created_by=user, **validated_data)
        for it in items_data:
            PurchaseItem.objects.create(purchase_order=po, **it)
        return po

    def update(self, instance, validated_data):
        # basic update that allows status changes to 'received' — on receiving, create Batches and StockTransactions
        items_data = validated_data.pop("items", None)
        status = validated_data.get("status", instance.status)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if items_data is not None:
            # for simplicity: clear existing and recreate; in production handle diffs
            instance.items.all().delete()
            for it in items_data:
                PurchaseItem.objects.create(purchase_order=instance, **it)

        # if status changed to received, create batches and stock transactions
        if instance.status == PurchaseOrder.STATUS_RECEIVED:
            for item in instance.items.all():
                med = item.medicine
                batch = med.batches.create(
                    batch_number=item.batch_number or f"po-{instance.pk}-{item.pk}",
                    quantity=item.quantity,
                    available_quantity=item.quantity,
                    purchase_price=item.purchase_price,
                    supplier=instance.supplier,
                    received_date=instance.created_at.date(),
                )
                # create stock transaction
                StockTransaction.objects.create(
                    medicine=med,
                    batch=batch,
                    transaction_type=StockTransaction.TYPE_IN,
                    quantity=item.quantity,
                    performed_by=instance.created_by,
                    note=f"Received via PO#{instance.pk}"
                )
        return instance

class StockTransactionSerializer(serializers.ModelSerializer):
    medicine_detail = MedicineSerializer(source="medicine", read_only=True)
    performed_by = serializers.ReadOnlyField(source="performed_by.email")

    class Meta:
        model = StockTransaction
        fields = ("id", "medicine", "medicine_detail", "batch", "transaction_type", "quantity", "note", "performed_by", "performed_at")
        read_only_fields = ("performed_at", "performed_by")
