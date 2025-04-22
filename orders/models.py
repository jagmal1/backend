import mongoengine as me
from users.models import Consumer, Farmer
from products.models import Product
import datetime

class Order(me.Document):
    order_id = me.StringField(unique=True, required=True)
    order_date = me.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    order_status = me.StringField()
    payment_status = me.StringField()
    delivery_status = me.StringField()
    consumer = me.ReferenceField(Consumer, required=True)
    products = me.ListField(me.ReferenceField(Product))
    farmers = me.ListField(me.ReferenceField(Farmer))

    meta = {'collection': 'orders'}
