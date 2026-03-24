from django.urls import path
from .views.landing_views import CustomLoginView

from .views.landing_views import LandingPageView, RegisterView

from .views.store_views import select_store
from .views.logout_views import custom_logout
from .views.store_views import StoreListView, StoreCreateView, StoreDeleteView
from .views.supplier_views import SupplierCreateView, SupplierDeleteView, SupplierListView, SupplierUpdateView
from .views.product_views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, product_suppliers_view
from .views.category_views import CategoryListView, CategoryCreateView, CategoryDeleteView, CategoryUpdateView
from .views.product_variant_views import ProductVariantListView, ProductVariantCreateView, ProductVariantUpdateView, ProductVariantDeleteView
from .views.purchase_views import PurchaseItemCreateView, PurchaseItemListView, PurchaseItemUpdateView, PurchaseItemDeleteView, PurchaseListView, PurchaseCreateView, PurchaseUpdateView
from .views.sale_views import SaleListView, SaleCreateView, SaleItemListView, SaleItemCreateView, SaleItemUpdateView, SaleItemDeleteView
from .views.inventory_views import InventoryListView
from .views.dashboard_views import DashboardView




urlpatterns = [

  path('', LandingPageView.as_view(),  name='landing'),
  
  path('login/', CustomLoginView.as_view(), name='login'),
  path('logout/', custom_logout, name='logout'),
  path('select-store/', select_store, name='select_store'),
  path('register/', RegisterView.as_view(), name= "register"),


  path('stores/', StoreListView.as_view(), name='show_store'),
  path('stores/add/', StoreCreateView.as_view(), name='store_add'),
  path('stores/<int:pk>/delete/', StoreDeleteView.as_view(), name='store_delete'),
  
  path('products/', ProductListView.as_view(), name="product_list"),
  path('products/add/', ProductCreateView.as_view(), name="product_add"),
  path('products/<int:pk>/update/', ProductUpdateView.as_view(), name="product_update"),
  path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name="product_delete"),

  path('categories/', CategoryListView.as_view(), name="category_list"),
  path('categories/add/', CategoryCreateView.as_view(), name="category_add"),
  path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name="category_update"),
  path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name="category_delete"),

  path('variants/', ProductVariantListView.as_view(), name="product_variant_list"),
  path('variants/add/', ProductVariantCreateView.as_view(), name="product_variant_add"),
  path('variants/<int:pk>/update/', ProductVariantUpdateView.as_view(), name="product_variant_update"),
  path('variants/<int:pk>/delete/', ProductVariantDeleteView.as_view(), name="product_variant_delete"),
  
  path('suppliers/', SupplierListView.as_view(), name="supplier_list"),
  path('suppliers/add/', SupplierCreateView.as_view(), name="supplier_add"),
  path('suppliers/<int:pk>/update/', SupplierUpdateView.as_view(), name="supplier_update"),
  path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name="supplier_delete"),

  path('purchases/', PurchaseListView.as_view(), name="purchase_list"),
  path('purchases/add/', PurchaseCreateView.as_view(), name="purchase_add"),
  path('purchases/<int:pk>/update/', PurchaseUpdateView.as_view(), name="purchase_update"),
  #path('purchases/<int:pk>/delete/', PurchaseDeleteView.as_view(), name="purchase_delete"),

  path('purchase-items/', PurchaseItemListView.as_view(), name="purchase_item_list"),
  path('purchase-items/add/', PurchaseItemCreateView.as_view(), name="purchase_item_add"),
  path('purchase-items/<int:pk>/update/', PurchaseItemUpdateView.as_view(), name="purchase_item_update"),
  path('purchase-items/<int:pk>/delete/', PurchaseItemDeleteView.as_view(), name="purchase_item_delete"),

  path("sales/", SaleListView.as_view(), name="sale_list"),
  path("sales/add/", SaleCreateView.as_view(), name="sale_add"),
  # path("sales/<int:pk>/update/", SaleUpdateView.as_view(), name="sale_update"),
  # path("sales/<int:pk>/delete/", SaleDeleteView.as_view(), name="sale_delete"),

  path("sale-items/", SaleItemListView.as_view(), name="sale_item_list"),
  path("sale-items/add/", SaleItemCreateView.as_view(), name="sale_item_add"),
  path("sale-items/<int:pk>/update/", SaleItemUpdateView.as_view(), name="sale_item_update"),
  path("sale-items/<int:pk>/delete/", SaleItemDeleteView.as_view(), name="sale_item_delete"),

  path("inventories/", InventoryListView.as_view(), name="inventory_list"),
  path('dashboard/', DashboardView.as_view(), name='dashboard'),
  path('products/<int:product_id>/suppliers/', product_suppliers_view, name='product_suppliers'),
  

]