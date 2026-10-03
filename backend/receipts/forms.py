from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from .models import DUPLICATE_RECEIPT_MESSAGE, MIN_RECEIPT_AMOUNT, Receipt


class ReceiptForm(forms.ModelForm):
    """Форма регистрации чека.

    Вся серверная валидация живёт в валидаторах модели (период акции, минимальная
    сумма, формат ФН/ФД/ФП) и в UniqueConstraint (ModelForm вызывает
    validate_constraints()). Статус и пользователь в форму не входят: их
    выставляет view, клиент на них повлиять не может.
    """

    class Meta:
        model = Receipt
        fields = ["fn", "fd", "fp", "purchased_at", "amount"]
        widgets = {
            "fn": forms.TextInput(
                attrs={"inputmode": "numeric", "autocomplete": "off"}
            ),
            "fd": forms.NumberInput(attrs={"min": 1, "autocomplete": "off"}),
            "fp": forms.TextInput(
                attrs={"inputmode": "numeric", "autocomplete": "off"}
            ),
            "purchased_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "amount": forms.NumberInput(
                attrs={"min": str(MIN_RECEIPT_AMOUNT), "step": "0.01"}
            ),
        }
        # Единое понятное сообщение о дубле: Django сам формирует ошибку
        # уникальности по коду "unique_together" (зависит от версии Django,
        # поэтому дублируем сообщение и в violation_error_message модели).
        error_messages = {
            NON_FIELD_ERRORS: {"unique_together": DUPLICATE_RECEIPT_MESSAGE},
        }