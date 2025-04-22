from bson import ObjectId
from auth_backend import protected_route
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from db_connection import products_collection
from auth_backend import protected_route  
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from PIL import Image


@csrf_exempt
@protected_route
def get_products(request):
    """Fetch all products for customers"""
    if request.method == "GET":
        products = list(products_collection.find({}))

        for product in products:
            product["_id"] = str(product["_id"])

        return JsonResponse(products, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@protected_route
def get_farmer_products(request):
    """Fetch only the logged-in farmer's products"""
    if request.method == "GET":
        if request.user_role != "farmer":
            return JsonResponse({"error": "Access denied"}, status=403)

        products = list(products_collection.find(
            {"farmer_email": request.user_email}))
        
        for product in products:
            product["_id"] = str(product["_id"])

        return JsonResponse(products, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)


# ✅ Function to compress the image
def compress_image(image, quality=70):
    img = Image.open(image)
    img = img.convert("RGB")  # Convert to RGB if not already
    img_io = BytesIO()
    img.save(img_io, format="JPEG", quality=quality)  # Adjust quality
    img_io.seek(0)  # Move pointer to start
    return img_io


@csrf_exempt
@protected_route
def add_product(request):
    """Add a new product"""
    if request.method == "POST":
        if request.content_type.startswith("multipart/form-data"):
            name = request.POST.get("name")
            price = request.POST.get("price")
            country = request.POST.get("country")
            pincode = request.POST.get("pincode")
            is_available = request.POST.get("available") == "true"
            image = request.FILES.get("image")

            if not name or not price or not country or not pincode or not image:
                return JsonResponse({"error": "Missing fields"}, status=400)

            ext = os.path.splitext(image.name)[-1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = f"uploads/{unique_filename}"
            saved_path = default_storage.save(
                file_path, ContentFile(image.read()))
            image_url = request.build_absolute_uri(f"/media/{saved_path}")

            product = {
                "name": name,
                "price": price,
                "image_url": image_url,
                "country": country,
                "pincode": pincode,
                "farmer_email": request.user_email,
                "is_available": is_available
            }

            products_collection.insert_one(product)
            return JsonResponse({"message": "Product added successfully", "image_url": image_url})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@protected_route
def update_availability(request):
    """Update product availability"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            is_available = data.get("is_available")

            if not product_id or is_available is None:
                return JsonResponse({"error": "Product ID and availability status required"}, status=400)

            product = products_collection.find_one(
                {"_id": ObjectId(product_id), "farmer_email": request.user_email})

            if not product:
                return JsonResponse({"error": "Product not found or unauthorized"}, status=404)

            # ✅ Update the availability status
            products_collection.update_one(
                {"_id": ObjectId(product_id)}, {
                    "$set": {"is_available": is_available}}
            )

            return JsonResponse({"message": "Product availability updated successfully"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
@protected_route
def delete_product(request, product_id):
    """Delete a product"""
    if request.method == "DELETE":
        try:
            object_id = ObjectId(product_id)  # Convert to ObjectId
            result = products_collection.delete_one({"_id": object_id})

            if result.deleted_count == 0:
                return JsonResponse({"error": "Product not found"}, status=404)

            return JsonResponse({"message": "Product deleted"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
