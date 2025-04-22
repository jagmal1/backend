from django.urls import path
from .views import get_products, get_farmer_products, add_product, update_availability, delete_product

urlpatterns = [
    path("", get_products, name="get_products"),
    path("farmer/", get_farmer_products, name="get_farmer_products"),
    path("farmer/add-product/", add_product, name="add_product"),
    path("farmer/update-availability/",update_availability, name="update_availability"),
    path("farmer/delete/<str:product_id>/",
         delete_product, name="delete_product"),
]
