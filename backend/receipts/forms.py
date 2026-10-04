from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _

from .models import DUPLICATE_RECEIPT_MESSAGE, MIN_RECEIPT_AMOUNT, Receipt


class ReceiptForm(forms.ModelForm):
    """Форма регистрации чека."""

    PLACEHOLDERS = {
        "fn": _("Введите ФН"),
        "fd": _("Введите номер чека (ФД)"),
        "fp": _("Введите ФП"),
        "purchased_at": _("дд.мм.гггг чч:мм"),
        "amount": _("0.00"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = ["form-input"]
            if name == "amount":
                css.append("form-input--amount")
            if self.is_bound and self.errors.get(name):
                css.append("form-input--error")
            field.widget.attrs["class"] = " ".join(css)
            placeholder = self.PLACEHOLDERS.get(name)
            if placeholder:
                field.widget.attrs.setdefault("placeholder", placeholder)

    class Meta:
        model = Receipt
        fields = ["fn", "fd", "fp", "purchased_at", "amount"]
        labels = {
            "fn": _("ФН"),
            "fd": _("Номер чека"),
            "fp": _("ФП"),
            "purchased_at": _("Дата покупки"),
            "amount": _("Сумма"),
        }
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

        error_messages = {
            NON_FIELD_ERRORS: {"unique_together": DUPLICATE_RECEIPT_MESSAGE},
        }