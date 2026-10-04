from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from .models import Receipt


class UserReceiptListApiView(LoginRequiredMixin, View):
    """API: список чеков текущего пользователя в JSON."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        receipts = (
            Receipt.objects
            .filter(user=request.user)
            .only(
                "id",
                "fn",
                "fd",
                "fp",
                "purchased_at",
                "amount",
                "status",
                "rejection_reason",
                "created_at",
            )
            .order_by("-created_at")
        )

        data = [
            {
                "id": r.id,
                "fn": r.fn,
                "fd": r.fd,
                "fp": r.fp,
                "purchased_at": r.purchased_at.isoformat() if r.purchased_at else None,
                "amount": str(r.amount),
                "status": r.status,
                "status_display": r.get_status_display(),
                "rejection_reason": r.rejection_reason or "",
                "created_at": r.created_at.isoformat(),
            }
            for r in receipts
        ]

        return JsonResponse({"receipts": data})
