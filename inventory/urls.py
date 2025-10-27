from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    SupplierListCreateView, SupplierDetailView,
    MedicineListCreateView, MedicineDetailView,
    BatchListCreateView, BatchDetailView,
    PurchaseOrderListCreateView, PurchaseOrderDetailView,
    StockTransactionListCreateView, LowStockListView
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category_list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),

    path("suppliers/", SupplierListCreateView.as_view(), name="supplier_list"),
    path("suppliers/<int:pk>/", SupplierDetailView.as_view(), name="supplier_detail"),

    path("medicines/", MedicineListCreateView.as_view(), name="medicine_list"),
    path("medicines/<int:pk>/", MedicineDetailView.as_view(), name="medicine_detail"),

    path("batches/", BatchListCreateView.as_view(), name="batch_list"),
    path("batches/<int:pk>/", BatchDetailView.as_view(), name="batch_detail"),

    path("purchase-orders/", PurchaseOrderListCreateView.as_view(), name="po_list"),
    path("purchase-orders/<int:pk>/", PurchaseOrderDetailView.as_view(), name="po_detail"),

    path("stock-transactions/", StockTransactionListCreateView.as_view(), name="stock_transactions"),
    path("low-stock/", LowStockListView.as_view(), name="low_stock"),
]
