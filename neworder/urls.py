from django.urls import path
from .import views
urlpatterns = [
    path('items/', views.ItemView.as_view()),
    path('order/', views.OrderView.as_view()),
    path("vieworder/customer/",views.ViewOrderCustomer.as_view()),
    path("vieworder/items/",views.ViewOrderItems.as_view()),
    path("history/estimated/",views.HistoryEstimatedView.as_view()),
    path("history/order/",views.HistoryOrderView.as_view())
]
