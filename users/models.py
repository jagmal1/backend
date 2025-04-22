import mongoengine as me


class Consumer(me.Document):
    consumer_id = me.StringField(unique=True, required=True)
    name = me.StringField(required=True)
    email = me.EmailField(required=True, unique=True)
    address = me.StringField()
    orders = me.ListField(me.ReferenceField("Order"))

    meta = {'collection': 'consumers'}


class Farmer(me.Document):
    farmer_id = me.StringField(unique=True, required=True)
    name = me.StringField(required=True)
    location = me.StringField()
    products = me.ListField(me.ReferenceField("Product"))
    orders = me.ListField(me.ReferenceField("Order"))

    meta = {'collection': 'farmers'}
