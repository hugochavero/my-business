from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from decimal import Decimal
from common.mixins import ModelAdminMixin, ReadOnlyModel
from ..constants import (
    SellOperationErrors,
    SellItemErrors,
    AccountKind,
    ExpenseOperationCategory,
    BuyOperationErrors,
)
from .base import TimeStampModel
from .core import Product


__all__ = (
    "SellOperation",
    "BuyOperation",
    "TransferOperation",
    "ExtractOperation",
    "SellItem",
    "ItemIncome",
    "Account",
    "SellOperationAccount",
)


class Account(TimeStampModel, ModelAdminMixin):
    name = models.CharField(max_length=255)
    kind = models.CharField(
        choices=AccountKind.CHOICES, default=AccountKind.CASH, max_length=255
    )
    is_business = models.BooleanField(default=True)
    balance = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.name} - {self.get_kind_display()} -> {self.balance}"

    def register_income(self, amount):
        self.balance += amount
        self.save()

    def register_extract(self, amount):
        # TODO: Allow negative balance ??
        self.balance -= amount
        self.save()


class BaseOperation(TimeStampModel, ModelAdminMixin):
    class Meta:
        abstract = True

    target_accounts = models.ManyToManyField(
        Account, related_name="%(app_label)s_%(class)s_target_account"
    )
    source_accounts = models.ManyToManyField(
        Account, related_name="%(app_label)s_%(class)s_source_account"
    )
    operation_date = models.DateField("Fecha de Operacion", default=timezone.now)


class SellOperation(BaseOperation):
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    profit = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.id}: Venta por {self.amount}"

    @classmethod
    def get_values_by_date_range(cls, date_from, date_to):
        """
        Get sum of cost, profit and amount in the given date range
        """
        operations = cls.objects.filter(operation_date__range=(date_from, date_to))
        return {
            "date_range": f"From {date_from} to {date_to}",
            "cost": operations.aggregate(models.Sum("sellitem__cost"))[
                "sellitem__cost__sum"
            ],
            "profit": operations.aggregate(models.Sum("sellitem__profit"))[
                "sellitem__profit__sum"
            ],
            "amount": operations.aggregate(models.Sum("sellitem__amount"))[
                "sellitem__amount__sum"
            ],
        }

    @classmethod
    def get_current_values_by_date(cls, date_from, date_to):
        """
        Get cost, amount and profit with current product's cost values
        """
        # TODO: Improve query
        operations = cls.objects.filter(operation_date__range=(date_from, date_to))
        cost = Decimal("0")
        profit = Decimal("0")
        amount = Decimal("0")
        for operation in operations:
            for item in operation.sellitem_set.all():
                amount += item.amount
                cost += Product.get_total_cost(item.qty, item.product_id)
                profit += amount - cost

        return {
            "date_range": f"From {date_from} to {date_to}",
            "cost": cost,
            "profit": profit,
            "amount": amount,
        }


class SellOperationAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    operation = models.ForeignKey(SellOperation, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def actions_pre_save(self):
        # Update balance in target accounts
        if self.id is None:
            self.account.register_income(self.amount)
            self.operation.target_accounts.add(self.account)

    def validations_pre_save(self):
        # TODO: This validation es needed ?
        if not self.operation.target_accounts.exists():
            raise ValidationError(SellOperationErrors.MISSING_TARGET_ACCOUNT)

    def save(self, **kwargs):
        self.actions_pre_save()
        super(SellOperationAccount, self).save(**kwargs)


class SellItem(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    operation = models.ForeignKey(SellOperation, on_delete=models.CASCADE)
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    profit = models.DecimalField(decimal_places=2, max_digits=10)

    def validations_post_save(self):
        # Update product's stock
        if self.qty > self.product.stock:
            raise ValidationError(
                SellItemErrors.INSUFFICIENT_STOCK.format(
                    self.product.title, self.qty, self.product.stock
                )
            )
        self.product.stock -= self.qty
        self.product.save()

    def save(self, **kwargs):
        self.cost = Product.get_total_cost(self.qty, self.product_id)
        self.amount = Product.get_total_price(self.qty, self.product_id)
        self.profit = self.amount - self.cost
        super().save(**kwargs)
        self.validations_post_save()


# TODO: change this approach to Income/Outcome models
class BuyOperation(BaseOperation):
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    observations = models.TextField(blank=True)

    def validations_post_save(self):
        itemincome_amount = 0
        # TODO: Improve query
        for item_income in self.itemincome_set.all():
            itemincome_amount += item_income.qty * item_income.product.price
        expenses_amount = (
            self.expenseoperation_set.aggregate(models.Sum("amount"))["amount__sum"]
            or 0
        )

        if self.amount != (itemincome_amount + expenses_amount):
            raise ValidationError(BuyOperationErrors.WRONG_SOURCE_ACCOUNT_AMOUNT)


class ItemIncome(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    operation = models.ForeignKey(BuyOperation, on_delete=models.CASCADE)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        return super(ItemIncome, self).save()
        # TODO: aqui debo crear el producto si no existe o actualizar el stock si existe


class ExpenseOperation(TimeStampModel):
    category = models.CharField(choices=ExpenseOperationCategory.CHOICES, max_length=50)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    operation = models.ForeignKey(BuyOperation, on_delete=models.CASCADE)


class TransferOperation(BaseOperation, ReadOnlyModel):
    amount = models.DecimalField(decimal_places=2, max_digits=10)


class ExtractOperation(BaseOperation):
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    cost = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    profit = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    period_from = models.DateField()
    period_to = models.DateField()
    observations = models.TextField(blank=True)
