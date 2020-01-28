from django.db import models
import uuid
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
    price = models.IntegerField()

    def __str__(self):
        return self.name




class Items(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tamil_name = models.TextField(null=True, blank=True)
    name = models.TextField()
    price = models.IntegerField()
    subitems = models.ManyToManyField(SubItems)

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.IntegerField()

    def __str__(self):
        return self.item.name

class OrderSubItem(models.Model):
    subitem = models.ForeignKey(SubItems,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.IntegerField()

    def __str__(self):
        return self.subitem.name

class Order(models.Model):
    invoice_no = models.TextField()
    confirmed = models.BooleanField(default=False)
    ordered_items = models.ManyToManyField(OrderItem)
    ordered_subitems = models.ManyToManyField(OrderSubItem)
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE)
    session = models.TextField()
    total = models.IntegerField()
    paid_amount = models.IntegerField()
    paid = models.BooleanField(default=False)
    returned_vessel = models.BooleanField(default=False)
    balance = models.IntegerField()
    date_placed = models.DateField(auto_now_add=True)
    date_of_delivery = models.DateField()

    def __str__(self):
        return self.invoice_no






#     def __str__(self):
#         return self.unique_id
