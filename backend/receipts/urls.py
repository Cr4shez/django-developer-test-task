from django.urls import path

from .views import ReceiptCreateView

urlpatterns = [
    path("", ReceiptCreateView.as_view(), name="receipt_create"),
]