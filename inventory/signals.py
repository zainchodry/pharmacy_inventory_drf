from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Batch, Medicine, StockTransaction
from django.db import models

def recompute_total_stock(medicine):
    total = medicine.batches.aggregate(total=models.Sum("available_quantity"))["total"] or 0
    medicine.total_stock = int(total)
    medicine.save(update_fields=["total_stock"])

@receiver(post_save, sender=Batch)
def batch_saved(sender, instance, created, **kwargs):
    # if batch created or available changed, recompute
    recompute_total_stock(instance.medicine)

@receiver(post_delete, sender=Batch)
def batch_deleted(sender, instance, **kwargs):
    recompute_total_stock(instance.medicine)

@receiver(post_save, sender=StockTransaction)
def handle_stock_transaction(sender, instance, created, **kwargs):
    if not created:
        return
    med = instance.medicine
    if instance.transaction_type == StockTransaction.TYPE_IN:
        # prefer to attach to existing batch if provided; otherwise create batch-less increase via a special batch
        if instance.batch:
            instance.batch.available_quantity = models.F('available_quantity') + instance.quantity
            instance.batch.save()
        else:
            # create a generic batch for this stock in
            b = med.batches.create(
                batch_number=f"autogen-{instance.pk}",
                quantity=instance.quantity,
                available_quantity=instance.quantity,
                purchase_price=0.00,
            )
            instance.batch = b
            instance.save(update_fields=["batch"])
    elif instance.transaction_type == StockTransaction.TYPE_OUT:
        if instance.batch:
            # consume from provided batch
            if instance.batch.available_quantity < instance.quantity:
                # allow negative? better raise, but to avoid crash, set to 0 and consume rest from other batches
                raise ValueError("Not enough quantity in selected batch")
            instance.batch.available_quantity = models.F('available_quantity') - instance.quantity
            instance.batch.save()
        else:
            # consume from earliest-expiring batches by FIFO
            remaining = instance.quantity
            batches = med.batches.filter(available_quantity__gt=0).order_by("expiry_date", "received_date")
            for b in batches:
                if remaining <= 0:
                    break
                take = min(int(b.available_quantity), remaining)
                b.available_quantity = models.F('available_quantity') - take
                b.save()
                remaining -= take
            if remaining > 0:
                raise ValueError("Not enough stock to consume requested quantity")
    elif instance.transaction_type == StockTransaction.TYPE_ADJUST:
        # adjustments should provide positive/negative quantity; apply to batch if present else adjust total via a synthetic batch
        if instance.batch:
            instance.batch.available_quantity = models.F('available_quantity') + instance.quantity
            instance.batch.save()
        else:
            # create synthetic batch for adjustment
            b = med.batches.create(
                batch_number=f"adjust-{instance.pk}",
                quantity=max(0, instance.quantity),
                available_quantity=max(0, instance.quantity),
                purchase_price=0.00,
            )
            instance.batch = b
            instance.save(update_fields=["batch"])
    # finally recompute totals
    recompute_total_stock(med)
