from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import jwt
import datetime
from db_connection import users_collection
from auth_backend import protected_route


SECRET_KEY = "your_secret_key"


@csrf_exempt
@protected_route
def auth_me(request):
    """Return authenticated user details"""
    return JsonResponse({
        "email": request.user_email,
        "role": request.user_role
    })


@csrf_exempt
def register(request):
    """Registers a user in MongoDB"""
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        if users_collection.find_one({"email": data["email"]}):
            return JsonResponse({"error": "Email already exists"}, status=400)

        hashed_password = make_password(data["password"])
        users_collection.insert_one({
            "email": data["email"],
            "password": hashed_password,
            "role": data["role"]  # ✅ 'customer' or 'farmer'
        })
        return JsonResponse({"message": "User registered successfully"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def login(request):
    """Authenticates user and returns JWT token"""
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        user = users_collection.find_one({"email": data["email"]})
        if not user or not check_password(data["password"], user["password"]):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        payload = {
            "email": data["email"],
            "role": user["role"],  # ✅ Send role in token
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return JsonResponse({"token": token, "role": user["role"], "email": data["email"]})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@protected_route
def logout(request):
    return JsonResponse({"message": "Logged out successfully"})
