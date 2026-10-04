from django.urls import path

from .views import ReceiptAddView

urlpatterns = [
    path("", ReceiptAddView.as_view(), name="receipt_add"),
    path("list/", ReceiptAddView.as_view(), name="receipt_list"),
]