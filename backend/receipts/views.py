from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView

from .forms import ReceiptForm
from .models import DUPLICATE_RECEIPT_MESSAGE, Receipt


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = "receipts/receipt_form.html"
    success_url = reverse_lazy("receipt_create")

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Новый чек всегда попадает «на проверку», что бы ни пришло в запросе
        form.instance.status = Receipt.Status.PENDING

        try:
            # savepoint: IntegrityError не должен ломать внешнюю транзакцию
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            # Гонка: два одинаковых чека прошли проверку формы одновременно,
            # а UniqueConstraint в БД остановил второй. Вместо 500 — ошибка формы.
            form.add_error(None, DUPLICATE_RECEIPT_MESSAGE)
            return self.form_invalid(form)

        messages.success(
            self.request, _("Чек принят и отправлен на проверку. Спасибо!")
        )
        return HttpResponseRedirect(self.get_success_url())
