from functools import wraps  # ✅ For authentication decorator
from django.http import JsonResponse
import jwt


SECRET_KEY = "your_secret_key"

def protected_route(view_func):
    """Decorator for protecting routes with JWT authentication"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_email = decoded["email"]
            request.user_role = decoded["role"]
        except Exception as e:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper
