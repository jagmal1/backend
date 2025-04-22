from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from db_connection import orders_collection, products_collection, cart_collection
from auth_backend import protected_route


@csrf_exempt
@protected_route
def create_order(request):
    """Create a new order from the user's cart"""
    if request.method == "POST":
        data = json.loads(request.body)
        user_email = request.user_email  # Get email from authenticated user

        # Fetch the cart for the user
        user_cart = cart_collection.find_one({"user_email": user_email})

        if not user_cart or not user_cart.get("items"):
            return JsonResponse({"error": "Cart is empty"}, status=400)

        # Get full_name & address from frontend
        full_name = data.get("full_name", "")
        address = data.get("address", "")
        payment_method = data.get("payment_method", "Cash on delivery")

        # Create order
        order = {
            "customer_email": user_email,
            "full_name": full_name,
            "address": address,
            "payment_method": payment_method,
            "items": user_cart["items"],  # Get items from cart
            "status": "Pending",
            # Default to 0 if missing
            "total_price": user_cart.get("total_price", 0)
        }

        # Insert order into database
        orders_collection.insert_one(order)

        # Clear the user's cart after placing the order
        cart_collection.update_one({"user_email": user_email}, {
                                   "$set": {"items": [], "total_price": 0}})

        return JsonResponse({"message": "Order placed successfully"}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)


@protected_route
def farmer_orders(request, farmer_email):
    """Fetch all orders for a farmer's products"""
    # Find all product IDs owned by the farmer
    farmer_products = list(products_collection.find(
        {"farmer_email": farmer_email}, {
            "_id": 1, "image_url": 1, "name": 1, "pincode": 1}  # Include image and name
    ))

    product_map = {str(p["_id"]): {"image_url": p["image_url"],
                                   "name": p["name"], "pincode":p["pincode"]} for p in farmer_products}
    product_ids = list(product_map.keys())

    # Find orders containing those products
    orders = list(orders_collection.find(
        {"items.product_id": {"$in": product_ids}}
    ))

    response_data = [
        {
            "_id": str(order["_id"]),
            "full_name": order["full_name"],
            "address": order["address"],
            "status": order["status"],
            "total_price": order["total_price"],
            "payment_method": order["payment_method"],
            "items": [
                {
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "image_url": product_map.get(item["product_id"], {}).get("image_url", ""),
                    "name": product_map.get(item["product_id"], {}).get("name", "Unknown Product"),
                    "pincode": product_map.get(item["product_id"], {}).get("pincode", "Unknown Pincode")
                }
                for item in order["items"]
            ],
        }
        for order in orders
    ]

    return JsonResponse(response_data, safe=False)


@csrf_exempt
@protected_route
def confirm_order(request, order_id):
    """Allow a farmer to confirm an order"""
    if request.method == "POST":
        order = orders_collection.find_one({"_id": ObjectId(order_id)})

        if not order:
            return JsonResponse({"error": "Order not found"}, status=404)

        # Ensure order is in Pending state before confirming
        if order["status"] != "Pending":
            return JsonResponse({"error": "Order cannot be confirmed"}, status=400)

        # Update order status to Confirmed
        orders_collection.update_one(
            {"_id": ObjectId(order_id)}, {"$set": {"status": "Confirmed"}}
        )

        return JsonResponse({"message": "Order confirmed successfully"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


@protected_route
def customer_orders(request, customer_email):
    """Fetch all orders placed by a specific customer"""

    # Fetch all orders for the customer
    orders = list(orders_collection.find({"customer_email": customer_email}))

    # Extract unique product IDs from all orders & convert to ObjectId
    product_ids = {ObjectId(item["product_id"])
                   for order in orders for item in order["items"]}

    # Fetch product details from products_collection
    products = list(products_collection.find(
        {"_id": {"$in": list(product_ids)}}))

    # Create a dictionary for fast lookup
    product_map = {
        str(p["_id"]): {"image_url": p.get("image_url", ""), "name": p.get("name", "Unknown Product")}
        for p in products
    }

    print("Fetched Products:", product_map)  # Debugging line

    # Construct response data
    response_data = [
        {
            "_id": str(order["_id"]),
            "address": order["address"],
            "status": order["status"],
            "total_price": order["total_price"],
            "payment_method": order["payment_method"],
            "items": [
                {
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "image_url": product_map.get(str(item["product_id"]), {}).get("image_url", ""),
                    "name": product_map.get(str(item["product_id"]), {}).get("name", "Unknown Product"),
                }
                for item in order["items"]
            ],
        }
        for order in orders
    ]

    return JsonResponse(response_data, safe=False)
