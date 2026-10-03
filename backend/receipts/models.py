from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as l_

MIN_RECEIPT_AMOUNT = Decimal("1000")

DUPLICATE_RECEIPT_MESSAGE = l_(
    "Этот чек уже зарегистрирован: чек с такими ФН, ФД и ФП уже есть в системе."
)


def validate_purchase_date(value):
    """Дата покупки должна входить в период акции (границы из .env, включительно)."""
    local_value = timezone.localtime(value) if timezone.is_aware(value) else value
    start = settings.PROMO_START_DATE
    end = settings.PROMO_END_DATE

    if start <= local_value.date() <= end:
        return

    raise ValidationError(
        l_("Дата покупки должна входить в период акции: с %(start)s по %(end)s."),
        code="outside_promo_period",
        params={
            "start": start.strftime("%d.%m.%Y"),
            "end": end.strftime("%d.%m.%Y"),
        },
    )


class Receipt(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", l_("На проверке")
        ACCEPTED = "accepted", l_("Принят")
        REJECTED = "rejected", l_("Отклонен")

    fn = models.CharField(
        l_("ФН"),
        max_length=16,
        validators=[
            RegexValidator(r"^\d{16}$", l_("ФН должен состоять ровно из 16 цифр.")),
        ],
        help_text=l_("Номер фискального накопителя, 16 цифр"),
    )
    fd = models.PositiveBigIntegerField(
        l_("ФД"),
        validators=[
            MinValueValidator(1, l_("ФД должен быть положительным числом.")),
            MaxValueValidator(9_999_999_999, l_("ФД не может быть длиннее 10 цифр.")),
        ],
        help_text=l_("Номер фискального документа, до 10 цифр"),
    )
    fp = models.CharField(
        l_("ФП"),
        max_length=10,
        validators=[
            RegexValidator(r"^\d{10}$", l_("ФП должен состоять ровно из 10 цифр.")),
        ],
        help_text=l_("Фискальный признак, 10 цифр"),
    )
    purchased_at = models.DateTimeField(
        l_("Дата и время покупки"),
        validators=[validate_purchase_date],
    )
    amount = models.DecimalField(
        l_("Сумма, ₽"),
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                MIN_RECEIPT_AMOUNT,
                l_("Сумма чека должна быть не меньше %(limit_value)s ₽."),
            ),
        ],
    )
    status = models.CharField(
        l_("Статус"),
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    rejection_reason = models.TextField(l_("Причина отказа"), blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name=l_("Пользователь"),
    )
    created_at = models.DateTimeField(l_("Дата регистрации"), auto_now_add=True)

    class Meta:
        verbose_name = l_("чек")
        verbose_name_plural = l_("чеки")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["fn", "fd", "fp"],
                name="unique_receipt_fn_fd_fp",
                violation_error_message=DUPLICATE_RECEIPT_MESSAGE,
            ),
        ]

    def __str__(self):
        return f"{self.fn} / {self.fd} / {self.fp}"