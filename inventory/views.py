from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Supplier, Medicine, Batch, PurchaseOrder, StockTransaction
from .serializers import (
    CategorySerializer, SupplierSerializer, MedicineSerializer, BatchSerializer,
    PurchaseOrderSerializer, StockTransactionSerializer
)
from django.db import models
from .permissions import IsPharmacistOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.db import transaction


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]

# Suppliers
class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "contact_email", "phone"]

class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]

# Medicines
class MedicineListCreateView(generics.ListCreateAPIView):
    queryset = Medicine.objects.prefetch_related("batches").all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "sku", "description"]
    filterset_fields = ["category", "is_active"]

class MedicineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medicine.objects.prefetch_related("batches").all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]

# Batches
class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.select_related("medicine", "supplier").all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["batch_number"]
    filterset_fields = ["medicine", "supplier"]

class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Batch.objects.select_related("medicine", "supplier").all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]

# Purchase Orders — create, update, receive
class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.prefetch_related("items__medicine").all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["supplier__name", "note"]
    filterset_fields = ["status"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PurchaseOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = PurchaseOrder.objects.prefetch_related("items__medicine").all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # allow update — serializer handles status==received actions
        return super().put(request, *args, **kwargs)

# Stock transactions - manual adjustments or consumption
class StockTransactionListCreateView(generics.ListCreateAPIView):
    queryset = StockTransaction.objects.select_related("medicine", "batch", "performed_by").all()
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["medicine__name", "note"]
    filterset_fields = ["transaction_type", "medicine"]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)

# Low stock / reorder alerts
class LowStockListView(APIView):
    permission_classes = [IsAuthenticated, IsPharmacistOrAdmin]

    def get(self, request):
        meds = Medicine.objects.filter(total_stock__lte=models.F("reorder_level"), is_active=True)
        data = MedicineSerializer(meds, many=True).data
        return Response(data)
