from django.urls import path
from .views import create_order, farmer_orders, confirm_order, customer_orders

urlpatterns = [
    path("create/", create_order, name="create_order"),
    path("farmer/<str:farmer_email>/", farmer_orders, name="farmer_orders"),
    path("confirm/<str:order_id>/", confirm_order, name="confirm_order"),
    path("customer/<str:customer_email>/",
         customer_orders, name="customer_orders"),
]
