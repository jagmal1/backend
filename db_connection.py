from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["foodfarma_db"]
users_collection = db["users"]
products_collection = db["products"]
cart_collection = db["cart"]
orders_collection = db["orders"]
