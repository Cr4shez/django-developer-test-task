from django.urls import path
from .views import ReceiptAddView, ReceiptListView
from .api import UserReceiptListApiView

urlpatterns = [
    path("", ReceiptAddView.as_view(), name="receipt_add"),
    path("list/", ReceiptListView.as_view(), name="receipt_list"),
    path("api/receipts/", UserReceiptListApiView.as_view(), name="api_user_receipts"),
]