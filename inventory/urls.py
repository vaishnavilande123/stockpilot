from django.urls import path
from .views.product_views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView

urlpatterns = [
  path('products/', ProductListView.as_view(), name="product-list"),
  path('products/add/', ProductCreateView.as_view(), name="product-add"),
  path('products/<int:pk>/update', ProductUpdateView.as_view(), name="product-update"),
  path('products/<int:pk>/delete', ProductDeleteView.as_view(), name="product-delete"),
  
]