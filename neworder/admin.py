from django.contrib import admin
from .models import *
# Register your models here.

# Register your models here.
admin.site.register(CustomerDetails)
admin.site.register(Items,ItemAdmin)
admin.site.register(SubItems,SubitemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(OrderSubItem)