import mongoengine as me
from users.models import Farmer


class Product(me.Document):
    product_id = me.StringField(unique=True, required=True)
    name = me.StringField(required=True)
    description = me.StringField()
    price = me.FloatField(required=True)
    quantity = me.IntField(required=True)
    category = me.StringField()
    farmer = me.ReferenceField(Farmer, required=True)
    orders = me.ListField(me.ReferenceField("Order"))

    meta = {'collection': 'products'}
