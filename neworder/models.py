from django.db import models
import uuid
from django.contrib import admin
# Customer Details Model


class CustomerDetails(models.Model):
    u_id = models.TextField()
    name = models.TextField()
    phone_number = models.TextField()
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name


class SubItems(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tamil_name = models.TextField(null=True, blank=True)
    name = models.TextField()
    price = models.FloatField()

    def __str__(self):
        return self.name


class SubitemAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class Items(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tamil_name = models.TextField(null=True, blank=True)
    name = models.TextField()
    price = models.FloatField()
    subitems = models.ManyToManyField(SubItems,blank=True)

    def __str__(self):
        return self.name

class ItemAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class OrderItem(models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.FloatField()
    total_price = models.FloatField()

    def __str__(self):
        return self.item.name

class OrderSubItem(models.Model):
    subitem = models.ForeignKey(SubItems,on_delete=models.CASCADE)
    quantity = models.FloatField()
    total_price = models.FloatField()

    def __str__(self):
        return self.subitem.name

class Order(models.Model):
    invoice_no = models.TextField()
    session = models.TextField(null=True)
    confirmed = models.BooleanField(default=False)
    hasGst = models.BooleanField(default=False)
    gst = models.TextField(null=True,blank=True)
    ordered_items = models.ManyToManyField(OrderItem)
    ordered_subitems = models.ManyToManyField(OrderSubItem)
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE)
    total = models.FloatField()
    paid_amount = models.FloatField()
    paid = models.BooleanField(default=False)
    returned_vessel = models.BooleanField(default=False)
    balance = models.FloatField()
    date_placed = models.DateField(auto_now_add=True)
    date_of_delivery = models.DateField()

    def __str__(self):
        return f"{self.invoice_no}-{self.customer.name}"




#     def __str__(self):
#         return self.unique_id
