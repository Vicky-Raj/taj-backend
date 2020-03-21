from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from .models import *
from django.http import HttpResponse
import uuid
import json
from . import writecsv
import datetime
from dateutil.parser import parse
import ast


def string_to_bool(value):
    if value.strip() == "true":
        return True
    elif value.strip() == "false":
        return False
    else:
        raise Exception("invalid string")

class ItemView(APIView):
    permission_classes = (AllowAny,)

    # Get Items

    def get(self, request):
        items = {}
        subitems = {}
        for item in Items.objects.all():
            items[item.name] = {
                "unique_id":item.unique_id,
                "price":item.price,
                "subitems":[subitem.name for subitem in item.subitems.all()]
            }
        for subitem in SubItems.objects.all():
            subitems[subitem.name] = {
                "unique_id":subitem.unique_id,
                "price":subitem.price
            }
        return Response({
            "items":items,
            "subitems":subitems
        })
    # Post New Item

    def post(self, request):
        item = Items()
        item.name = request.POST.get('name')
        item.price = request.POST.get('price')
        item.total_price = request.POST.get('total_price')
        subs = request.POST.get('subitems')
        for i in subs:
            subitem = SubItems()
            subitem.name = i['name']
            subitem.price = i['price']
            subitem.quantity = i['quantity']
            item.subitems.add(subitem)
            subitem.save()
        item.save()
        return Response({})

        # Edit Existing Item
    def put(self, request):
        item = get_object_or_404(Items, pk=int(request.POST.get('pk')))
        item.name = request.POST.get('name')
        item.price = int(request.POST.get('price'))
        item.total_price = int(request.POST.get('total_price'))
        subs = request.POST.get('subitems')
        for i in subs:
            subitem = SubItems()
            subitem.name = i['name']
            subitem.price = int(i['price'])
            subitem.quantity = int(i['quantity'])
            item.subitems.add(subitem)
            subitem.save()
        item.save()

        return Response({})
    # Delete Item

    def patch(self, request):
        item = get_object_or_404(Items, pk=int(request.POST.get('pk')))
        item.delete()
        return Response({})


class OrderView(APIView):
    permission_classes = (AllowAny,)
    # View Order

    def get(self, request):
        if request.GET.get("id"):
            orders = Order.objects.filter(invoice_no=request.GET.get("id"))


        return Response([
        {
            "invoiceNo":order.invoice_no,
            "session":order.session,
            "total":order.total,
            "paidAmount":order.paid_amount,
            "balance":order.balance,
            "paid":order.paid,
            "vessel":order.returned_vessel,
            "date":order.date_of_delivery,
            "confirmed":order.confirmed,
            "customer":{
                "name":order.customer.name,
                "phoneNo":order.customer.phone_number,
                "email":order.customer.email,
                "address":order.customer.address
            },
            "items":[
            {
                'unique_id': order_item.item.unique_id,
                'name': order_item.item.name,
                'price': order_item.item.price,
                "quantity":order_item.quantity,
                "totalPrice":order_item.total_price,
                'subitems': [subitem.name for subitem in order_item.item.subitems.all()]
            }
            for order_item in order.ordered_items.all()],
            "subitems":[
            {
                'unique_id': order_subitem.subitem.unique_id,
                'name': order_subitem.subitem.name,
                'price':order_subitem.subitem.price,
                "quantity":order_subitem.quantity,
                "totalPrice":order_subitem.total_price
            }
            for order_subitem in order.ordered_subitems.all()]
        }
        for order in orders])

    def post(self, request):

        
        info = json.loads(request.body)
        print(info)
        order = Order()
        order.invoice_no = f"{uuid.uuid4().time}"
        order.total = float(info["total"])
        order.paid_amount = float(info["advance"])
        order.balance = float(info["balance"])
        order.paid = float(info["balance"]) == 0
        order.date_of_delivery = parse(info["customer"]["date"])
        order.session = info["customer"]["session"]
        order.confirmed = info["confirm"]
        order.gst = info["gst"]
        order.hasGst = info["hasGst"]
        customer = CustomerDetails()
        customer.u_id = f"{uuid.uuid4()}"
        customer.name = info["customer"]["name"]
        customer.phone_number  = info["customer"]["phoneNo"]
        customer.email = info["customer"]["email"]
        customer.address = info["customer"]["address"]
        customer.save()
        order.customer = customer
        order.save()
        for item in info["items"]:
            current_item = Items.objects.filter(unique_id=item["unique_id"]).first()
            if not current_item:
                current_sub_item = SubItems.objects.filter(unique_id=item["unique_id"]).first()
                order_sub_item = OrderSubItem()
                order_sub_item.subitem = current_sub_item
                order_sub_item.quantity = float(item["quantity"])
                order_sub_item.total_price = float(item["amount"])
                order_sub_item.save()
                order.ordered_subitems.add(order_sub_item)
                order.save()
            else:
                order_item = OrderItem()
                order_item.item = current_item
                order_item.quantity = float(item["quantity"])
                order_item.total_price = float(item["amount"])
                order_item.save()
                order.ordered_items.add(order_item)
                order.save()

        writecsv.write_order_csv(
            {
                'InvoiceNo': order.invoice_no,
                'CustomerId': customer.u_id,
                'CustomerName': customer.name,
                'CustomerNumber': customer.phone_number,
                'TotalAmount': order.total
            }
        )

        return Response({
            "id":order.invoice_no
        })
    # Edit Order

    def put(self, request):
        info = json.loads(request.body);
        order = get_object_or_404(Order,invoice_no=info["id"])
        order.total = int(info["total"])
        order.paid_amount = int(info["advance"])
        order.balance = int(info["balance"])
        order.paid = int(info["paid"])
        order.returned_vessel = info["vessel"]
        order.date_of_delivery = parse(info["customer"]["date"])
        order.session = info["customer"]["session"]
        order.confirmed = info["confirmed"]
        order.save()

        order.customer.name = info["customer"]["name"]
        order.customer.phone_number  = info["customer"]["phoneNo"]
        order.customer.email = info["customer"]["email"]
        order.customer.address = info["customer"]["address"]
        order.customer.save()

        for item in order.ordered_items.all():
            item.delete()
        order.save()
        for subitem in order.ordered_subitems.all():
            subitem.delete()
        order.save()

        for item in info["items"]:
            current_item = get_object_or_404(Items,unique_id=item["unique_id"])
            order_item = OrderItem()
            order_item.item = current_item
            order_item.quantity = int(item["quantity"])
            order_item.total_price = int(item["amount"])
            order_item.save()
            order.ordered_items.add(order_item)
            order.save()

        for sub_item in info["subItems"]:
            current_sub_item = get_object_or_404(SubItems,unique_id=sub_item["unique_id"])
            order_sub_item = OrderSubItem()
            order_sub_item.subitem = current_sub_item
            order_sub_item.quantity = int(sub_item["quantity"])
            order_sub_item.total_price = int(sub_item["amount"])
            order_sub_item.save()
            order.ordered_subitems.add(order_sub_item)
            order.save()

        return Response()


    def patch(self, request):
        order = get_object_or_404(
            Order, invoice_no=request.POST.get('invoice_no'))
        order.delete()
        return Response({})


class ViewOrderCustomer(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        print(request.GET.get("confirmed"))
        if request.GET.get("session") != "ALL":
            orders = Order.objects.filter(
                date_of_delivery=parse(request.GET.get("date")),
                session=request.GET.get("session"),
                confirmed=string_to_bool(request.GET.get("confirmed"))
            )
        else:
            orders = Order.objects.filter(
                date_of_delivery=parse(request.GET.get("date")),
                confirmed=string_to_bool(request.GET.get("confirmed"))
            )
        return Response([
            {
                "name":order.customer.name,
                "phoneNo":order.customer.phone_number,
                "session":order.session,
                "invoiceNo":order.invoice_no
            }
        for order in orders])


def create_daily_item(orders,items):
    for order in orders:
        for order_item in order.ordered_items.all():
            if order_item.item.tamil_name in items:
                items[order_item.item.tamil_name] += order_item.quantity
            else:
                items[order_item.item.tamil_name] = order_item.quantity
        
        for order_subitem in order.ordered_subitems.all():
            if order_subitem.subitem.tamil_name in items:
                items[order_subitem.subitem.tamil_name] += order_subitem.quantity
            else:
                items[order_subitem.subitem.tamil_name] = order_subitem.quantity

class ViewOrderItems(APIView):
    permission_classes = (AllowAny,)

    def get(self,request):
        fn_items = {}
        an_items = {}
        evening_items = {}
        
        fn_orders = Order.objects.filter(
            date_of_delivery=parse(request.GET.get("date")),
            session="FN",
            paid=True,
            confirmed=True
        )
        an_orders = Order.objects.filter(
            date_of_delivery=parse(request.GET.get("date")),
            session="AN",
            paid=True,
            confirmed=True
        )
        evening_orders = Order.objects.filter(
            date_of_delivery=parse(request.GET.get("date")),
            session="EVENING",
            paid=True,
            confirmed=True
        )

        create_daily_item(fn_orders,fn_items)
        create_daily_item(an_orders,an_items)
        create_daily_item(evening_orders,evening_items)

        return Response({
            "fn":fn_items,
            "an":an_items,
            "evening":evening_items
        })

class HistoryEstimatedView(APIView):
    permission_classes = (AllowAny,)

    def get(self,request):
        orders = Order.objects.filter(
            confirmed = False,
            # date_of_delivery__lte= datetime.date.today,
            date_of_delivery = parse(request.GET.get("date"))
        )
        return Response([   
            {
                "invoice":order.invoice_no,
                "name":order.customer.name,
                "phoneno":order.customer.phone_number,
                "placed_date":order.date_placed,
                "delivery_date":order.date_of_delivery
            }
        for order in orders])

def create_customer_items(orders,customer_items):
    items = {}
    for order in orders:
        items["name"] = order.customer.name
        for order_item in order.ordered_items.all():
            if order_item.item.tamil_name in items:
                items[order_item.item.tamil_name] += order_item.quantity
            else:
                items[order_item.item.tamil_name] = order_item.quantity
        
        for order_subitem in order.ordered_subitems.all():
            if order_subitem.subitem.tamil_name in items:
                items[order_subitem.subitem.tamil_name] += order_subitem.quantity
            else:
                items[order_subitem.subitem.tamil_name] = order_subitem.quantity
        customer_items.append(items.copy());
        items.clear()

class ViewOrderItemsandCustomersView(APIView):
    permission_classes = (AllowAny,)

    def get(self,request):
        all_customer_items= []
        fn_customer_items= []
        an_customer_items = []
        evening_customer_items = []

        fn_items = Order.objects.filter(
            date_of_delivery=parse(request.GET.get("date")),
            session="FN"
        )
        an_items = Order.objects.filter(
            date_of_delivery=parse(request.GET.get("date")),
            session="AN"
        )
        evening_items = Order.objects.filter(
            date_of_delivery=parse(request.GET.get("date")),
            session="EVENING"
        )
        create_customer_items(fn_items,fn_customer_items)
        create_customer_items(an_items,an_customer_items)
        create_customer_items(evening_items,evening_customer_items)

        return Response({
            "fn":fn_customer_items,
            "an":an_customer_items,
            "evening":evening_customer_items,
        })


class HistoryOrderView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self,request):
        print(request.GET["date"])
        orders = Order.objects.filter(
            confirmed = True,
            # date_of_delivery__lte= datetime.date.today,
            paid=True,
            returned_vessel=True,
            date_of_delivery=parse(request.GET.get("date"))
        )
        print(orders)
        return Response([
            {
                "name":order.customer.name,
                "invoice_no":order.invoice_no,
                "session":order.session,
                "phone_num":order.customer.phone_number,
                "date_placed":order.date_placed,
                "date_of_delivery":order.date_of_delivery,
                "paid":order.paid,
                "hasGst":order.hasGst,
                "gst":order.gst,
                "returned_vessel":order.returned_vessel
            }
        for order in orders])

class HistoryAllOrder(APIView):
    permission_classes = (AllowAny,)
    
    def get(self,request):
        print(request.GET["gst"])
        if(string_to_bool(request.GET.get("gst"))):
            print("entered if")
            orders = Order.objects.filter(
                confirmed = True,
                date_of_delivery__lte= datetime.date.today(),
                hasGst = True,
            )
        else:
            orders = Order.objects.filter(
                confirmed = True,
                date_of_delivery__lte= datetime.date.today(),
            )
        return Response([
            {
                "name":order.customer.name,
                "invoice_no":order.invoice_no,
                "session":order.session,
                "phone_num":order.customer.phone_number,
                "date_placed":order.date_placed,
                "date_of_delivery":order.date_of_delivery,
                "paid":order.paid,
                "hasGst":order.hasGst,
                "gst":order.gst,
                "returned_vessel":order.returned_vessel
            }
        for order in orders])

class HistoryDateOrder(APIView):
    permission_classes = (AllowAny,)
    
    def get(self,request):
        if(string_to_bool(request.GET.get("gst"))):
            orders = Order.objects.filter(
                confirmed = True,
                hasGst = True,
                date_of_delivery__lte= datetime.date.today(),
                date_of_delivery=parse(request.GET.get("date"))
            )
        else:
            orders = Order.objects.filter(
                confirmed = True,
                date_of_delivery__lte= datetime.date.today(),
                date_of_delivery=parse(request.GET.get("date"))
            )
        return Response([
            {
                "name":order.customer.name,
                "invoice_no":order.invoice_no,
                "session":order.session,
                "phone_num":order.customer.phone_number,
                "date_placed":order.date_placed,
                "date_of_delivery":order.date_of_delivery,
                "paid":order.paid,
                "hasGst":order.hasGst,
                "gst":order.gst,
                "returned_vessel":order.returned_vessel
            }
        for order in orders])

class HistoryRangeOrder(APIView):
    permission_classes = (AllowAny,)
    
    def get(self,request):
        start_date = parse(request.GET.get("from")),
        end_date = parse(request.GET.get("to")), 
        if(string_to_bool(request.GET.get("gst"))):
            orders = Order.objects.filter(
                confirmed = True,
                hasGst = True,
                date_of_delivery__lte= datetime.date.today(),
                date_of_delivery__range=(start_date[0].date(),end_date[0].date()),           
            )
        else:
            orders = Order.objects.filter(
                confirmed = True,                
                date_of_delivery__lte= datetime.date.today(),
                date_of_delivery__range=(start_date[0].date(),end_date[0].date()),           
            )
            print(orders)
        return Response([
            {
                "name":order.customer.name,
                "invoice_no":order.invoice_no,
                "session":order.session,
                "phone_num":order.customer.phone_number,
                "date_placed":order.date_placed,
                "date_of_delivery":order.date_of_delivery,
                "paid":order.paid,
                "hasGst":order.hasGst,
                "gst":order.gst,
                "returned_vessel":order.returned_vessel
            }
        for order in orders])