from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardView, WarehouseViewSet, ProductCategoryViewSet,
    ProductBrandViewSet, ProductViewSet,
    UnitOfMeasureViewSet, ProductListAPIView, UnitOfMeasureListAPIView,
    UnitCategoryListAPIView, UnitCategoryViewSet, PriceTypeViewSet,
    ProductDataTableAPIView, ProductListDirectAPIView, ProductListProviderAPIView, ProductDefaultPriceAPIView, DefaultWarehouseAPIView,
    ProductBrandsListAPIView, ProductBrandsUpdateAPIView,
    # Nuevas vistas para dashboard mejorado
    TestDashboardAPIView, InventoryDashboardMetricsAPIView, TopSellingProductsAPIView, SalesAnalysisAPIView,
    LowStockProductsAPIView, LowestStockProductsAPIView,
    TopCustomersAPIView, TopSuppliersAPIView, CustomersSuppliersComparisonAPIView,
    ProductMovementsReportAPIView, ProductMovementsExportAPIView,
    # Export views
    SalesByProductExportAPIView, SalesByCustomerExportAPIView, SalesByPeriodExportAPIView, FinancialSummaryExportAPIView,
    # Stock Export views
    StockByWarehouseExportAPIView, CompleteStockExportAPIView, LowStockProductsExportAPIView, StockReportExportAPIView,
    # Customers & Suppliers Export views
    CustomersListExportAPIView, SuppliersListExportAPIView, ComparativeAnalysisExportAPIView, TrendsExportAPIView
)

from .views_validation import validate_units_of_measure

from .views_schema import (
    ProductCategorySchemaView, ProductBrandSchemaView,
    UnitOfMeasureSchemaView, UnitCategorySchemaView,
    PriceTypeSchemaView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'productcategory', ProductCategoryViewSet)
router.register(r'productbrand', ProductBrandViewSet)
router.register(r'products', ProductViewSet, basename='product')
router.register(r'unitsofmeasure', UnitOfMeasureViewSet, basename='unitofmeasure')
router.register(r'unitcategory', UnitCategoryViewSet)
router.register(r'pricetypes', PriceTypeViewSet)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='inventory-dashboard'),
    path('api/validate-units-measure/', validate_units_of_measure, name='validate-units-measure'),
    
    # Schema endpoints
    path('api/schema/product-category/', ProductCategorySchemaView.as_view(), name='product-category-schema'),
    path('api/schema/productcategory/', ProductCategorySchemaView.as_view()),  # alias alternativo
    path('api/schema/productbrand/', ProductBrandSchemaView.as_view(), name='productbrand-schema'),
    path('api/schema/unitofmeasure/', UnitOfMeasureSchemaView.as_view(), name='unitofmeasure-schema'),
    path('api/unitcategories/', UnitCategoryListAPIView.as_view(), name='unitcategory-list'),
    path('api/schema/unitcategory/', UnitCategorySchemaView.as_view(), name='unitcategory-schema'),
    path('api/schema/pricetype/', PriceTypeSchemaView.as_view(), name='pricetype-schema'),
    
    # List endpoints
    path('api/products/options/', ProductListAPIView.as_view(), name='product-list-options'),
    path('api/unitsofmeasure-options/', UnitOfMeasureListAPIView.as_view(), name='unitofmeasure-options'),
    path('api/datatable-products/', ProductDataTableAPIView.as_view(), name='datatable-products'),
    path('api/products-direct/', ProductListDirectAPIView.as_view(), name='products-direct'),
    path('api/products-provider/', ProductListProviderAPIView.as_view(), name='products-provider'),
    
    # New endpoints for auto-populating fields
    path('api/products/<int:product_id>/default-price/', ProductDefaultPriceAPIView.as_view(), name='product-default-price'),
    path('api/products/<int:product_id>/brands/', ProductBrandsListAPIView.as_view(), name='product-brands'),
    path('api/products/<int:product_id>/brands/update/', ProductBrandsUpdateAPIView.as_view(), name='product-brands-update'),
    path('api/default-warehouse/', DefaultWarehouseAPIView.as_view(), name='default-warehouse'),
    
    # Nuevas URLs para dashboard mejorado
    path('api/dashboard/test/', TestDashboardAPIView.as_view(), name='dashboard-test'),
    path('api/dashboard/metrics/', InventoryDashboardMetricsAPIView.as_view(), name='dashboard-metrics'),
    path('api/dashboard/top-selling-products/', TopSellingProductsAPIView.as_view(), name='top-selling-products'),
    path('api/dashboard/sales-analysis/', SalesAnalysisAPIView.as_view(), name='sales-analysis'),
    path('api/dashboard/low-stock-products/', LowStockProductsAPIView.as_view(), name='low-stock-products'),
    path('api/dashboard/lowest-stock-products/', LowestStockProductsAPIView.as_view(), name='lowest-stock-products'),
    path('api/dashboard/top-customers/', TopCustomersAPIView.as_view(), name='top-customers'),
    path('api/dashboard/top-suppliers/', TopSuppliersAPIView.as_view(), name='top-suppliers'),
    path('api/dashboard/customers-suppliers-comparison/', CustomersSuppliersComparisonAPIView.as_view(), name='customers-suppliers-comparison'),
    path('api/dashboard/product-movements/', ProductMovementsReportAPIView.as_view(), name='product-movements-report'),
    path('api/export/product-movements/', ProductMovementsExportAPIView.as_view(), name='export-product-movements'),
    
    # Export endpoints
    path('api/export/sales-by-product/', SalesByProductExportAPIView.as_view(), name='export-sales-by-product'),
    path('api/export/sales-by-customer/', SalesByCustomerExportAPIView.as_view(), name='export-sales-by-customer'),
    path('api/export/sales-by-period/', SalesByPeriodExportAPIView.as_view(), name='export-sales-by-period'),
    path('api/export/financial-summary/', FinancialSummaryExportAPIView.as_view(), name='export-financial-summary'),
    
    # Stock Export endpoints
    path('api/export/stock-by-warehouse/', StockByWarehouseExportAPIView.as_view(), name='export-stock-by-warehouse'),
    path('api/export/complete-stock/', CompleteStockExportAPIView.as_view(), name='export-complete-stock'),
    path('api/export/low-stock-products/', LowStockProductsExportAPIView.as_view(), name='export-low-stock-products'),
    path('api/export/stock-report/', StockReportExportAPIView.as_view(), name='export-stock-report'),
    
    # Customers & Suppliers Export endpoints
    path('api/export/customers-list/', CustomersListExportAPIView.as_view(), name='export-customers-list'),
    path('api/export/suppliers-list/', SuppliersListExportAPIView.as_view(), name='export-suppliers-list'),
    path('api/export/comparative-analysis/', ComparativeAnalysisExportAPIView.as_view(), name='export-comparative-analysis'),
    path('api/export/trends/', TrendsExportAPIView.as_view(), name='export-trends'),
    
    # CRUD API routes
    path('api/', include(router.urls)),
]
