from django.urls import path
from .views import ReceiptAddView, ReceiptListView

urlpatterns = [
    path("", ReceiptAddView.as_view(), name="receipt_add"),
    path("list/", ReceiptListView.as_view(), name="receipt_list"),
]