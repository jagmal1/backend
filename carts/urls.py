from django.urls import path
from .views import remove_from_cart, get_cart, add_to_cart

urlpatterns = [
    path("", get_cart, name="get_cart"),
    path("remove/", remove_from_cart, name="remove_from_cart"),
    path("add/", add_to_cart, name="add_to_cart"),
]
