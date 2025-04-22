from bson import ObjectId  
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from auth_backend import protected_route
from db_connection import cart_collection, products_collection


def convert_objectid_to_str(data):
    """Recursively convert ObjectId fields to strings"""
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
    

@csrf_exempt
@protected_route
def add_to_cart(request):
    """Add a product to the cart"""
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        # Ensure quantity is an integer
        quantity = int(data.get("quantity", 1))

        if not product_id:
            return JsonResponse({"error": "Product ID required"}, status=400)

        user_email = request.user_email

        # Fetch product details from the product collection
        product = products_collection.find_one({"_id": ObjectId(product_id)})

        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        # Ensure price is numeric
        product_price = float(product.get("price", 0))

        # Fetch user's cart
        cart = cart_collection.find_one({"user_email": user_email})

        if not cart:
            cart = {
                "user_email": user_email,
                "items": [],
                "total_price": 0
            }

        # Check if the product already exists in the cart
        product_exists = False
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                product_exists = True
                break

        # If product does not exist in the cart, add it
        if not product_exists:
            cart["items"].append({
                "product_id": product_id,
                "quantity": quantity,
                "price": product_price
            })

        # Calculate total price
        cart["total_price"] = sum(
            float(item.get("price", 0)) * int(item.get("quantity", 1)) for item in cart["items"]
        )

        # Update cart in MongoDB
        cart_collection.update_one({"user_email": user_email}, {
                                   "$set": cart}, upsert=True)

        # 🔥 Convert ObjectId to string before returning JSON
        cart = convert_objectid_to_str(cart)

        return JsonResponse({"message": "Product added to cart", "cart": cart}, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@protected_route
def get_cart(request):
    """Fetch user's cart"""
    if request.method == "GET":
        user_email = request.user_email
        cart = cart_collection.find_one({"user_email": user_email}, {"_id": 0})

        if not cart:
            return JsonResponse({"cart": {"items": [], "total_price": 0}})

        # Fetch image URLs for each item from MongoDB
        for item in cart.get("items", []):
            product = products_collection.find_one(
                {"_id": ObjectId(item["product_id"])})
            item["image_url"] = product["image_url"] if product and "image_url" in product else None

        return JsonResponse({"cart": cart})

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
@protected_route
def remove_from_cart(request):
    """Remove a product from the cart"""
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")

        if not product_id:
            return JsonResponse({"error": "Product ID required"}, status=400)

        user_email = request.user_email
        cart = cart_collection.find_one({"user_email": user_email})

        if not cart:
            return JsonResponse({"error": "Cart not found"}, status=404)

        # Remove product from cart
        cart["items"] = [item for item in cart["items"]
                         if item["product_id"] != product_id]
        cart["total_price"] = sum(item["price"] * item["quantity"]
                                  for item in cart["items"])

        # Update cart in MongoDB
        cart_collection.update_one({"user_email": user_email}, {"$set": cart})

        # 🔥 Convert entire cart structure to JSON serializable format
        cart = convert_objectid_to_str(cart)

        return JsonResponse({"message": "Item removed from cart", "cart": cart}, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)
