from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, ListView

from .forms import ReceiptForm
from .models import DUPLICATE_RECEIPT_MESSAGE, Receipt


class ReceiptListView(LoginRequiredMixin, ListView):
    model = Receipt
    template_name = "receipts/list.html"
    context_object_name = "receipts"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .only(
                "purchased_at",
                "status",
                "amount",
                "created_at",
                "rejection_reason",
            )
        )


class ReceiptAddView(LoginRequiredMixin, CreateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = "receipts/add.html"
    success_url = reverse_lazy("receipt_add")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = Receipt.Status.PENDING

        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            form.add_error(None, DUPLICATE_RECEIPT_MESSAGE)
            return self.form_invalid(form)

        if self.is_ajax_request():
            return JsonResponse(
                {"status": "ok", "message": _("Чек принят и отправлен на проверку. Спасибо!")},
                status=201
            )

        messages.success(
            self.request, _("Чек принят и отправлен на проверку. Спасибо!")
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.is_ajax_request():
            errors = {}
            for field_name, field_errors in form.errors.items():
                if field_name == "__all__":
                    errors["__all__"] = list(field_errors)
                else:
                    errors[field_name] = list(field_errors)
            return JsonResponse({"status": "error", "errors": errors}, status=422)
        return super().form_invalid(form)

    def is_ajax_request(self):
        return self.request.headers.get("x-requested-with") == "XMLHttpRequest"
