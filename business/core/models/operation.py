from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from common.mixins import ModelAdminMixin
from .validation import ValidationModelMixin
from ..constants import SellOperationErrors, SellItemErrors, AccountKind
from .base import TimeStampModel
from .core import Product


__all__ = (
    'SellOperation',
    'BuyOperation',
    'TransferOperation',
    'ExtractOperation',
    'SellItem',
    'BuyItem',
    'Account',
    'SellOperationAccount',
)


class Account(TimeStampModel, ModelAdminMixin):
    name = models.CharField(max_length=255)
    kind = models.CharField(choices=AccountKind.CHOICES, default=AccountKind.CASH, max_length=255)
    balance = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f'{self.name} - {self.get_kind_display()} -> {self.balance}'

    def register_income(self, amount):
        self.balance += amount
        self.save()

    def registar_extract(self, amount):
        # TODO: Allow negative balance ??
        self.balance -= amount
        self.save()


class BaseOperation(TimeStampModel):
    class Meta:
        abstract = True
    target_accounts = models.ManyToManyField(Account, related_name='%(app_label)s_%(class)s_target_account')
    source_accounts = models.ManyToManyField(Account, related_name='%(app_label)s_%(class)s_source_account', null=True)
    operation_date = models.DateField("Fecha de Operacion", default=timezone.now)


class SellOperation(BaseOperation, ModelAdminMixin):

    def __str__(self):
        return f'{self.id}: Venta por {self.amount}'

    @property
    def cost(self):
        return self.sellitem_set.aggregate(models.Sum('cost'))['cost__sum']

    @property
    def profit(self):
        return self.sellitem_set.aggregate(models.Sum('profit'))['profit__sum']

    @property
    def amount(self):
        return self.sellitem_set.aggregate(models.Sum('amount'))['amount__sum']

    def validations_post_save(self):
        if self.amount != self.selloperationaccount_set.aggregate(models.Sum('amount'))['amount__sum']:
            raise ValidationError(SellOperationErrors.WRONG_TARGET_ACCOUNTS_AMOUNT)

    @classmethod
    def get_values_by_date_range(cls, date_from, date_to):
        """
            Get sum of cost, profit and amount in the given date range
        """
        _query = cls.objects.filter(operation_date__range=(date_from, date_to))
        return {
            "date_range": f"From {date_from} to {date_to}",
            "cost": _query.aggregate(models.Sum('sellitem__cost'))['sellitem__cost__sum'],
            "profit": _query.aggregate(models.Sum('sellitem__profit'))['sellitem__profit__sum'],
            "amount": _query.aggregate(models.Sum('sellitem__amount'))['sellitem__amount__sum'],
        }


class SellOperationAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    operation = models.ForeignKey(SellOperation, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def actions_post_save(self):
        # Update balance in target accounts
        self.account.register_income(self.amount)
        self.operation.target_accounts.add(self.account)

    def validations_post_save(self):
        # TODO: This validation es needed ?
        if not self.operation.target_accounts.exists():
            raise ValidationError(SellOperationErrors.MISSING_TARGET_ACCOUNT)

    def save(self, **kwargs):
        super(SellOperationAccount, self).save(**kwargs)
        self.actions_post_save()
        self.validations_post_save()


class SellItem(TimeStampModel, ValidationModelMixin):
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
                SellItemErrors.INSUFFICIENT_STOCK.format(self.product.title, self.qty, self.product.stock)
            )
        self.product.stock -= self.qty
        self.product.save()

    def save(self, **kwargs):
        # self.cost = self.qty * self.product_set.aggregate(cost=Sum('cost')).values('cost')
        self.cost = Product.get_total_cost(self.qty, self.product_id)
        self.amount = Product.get_total_price(self.qty, self.product_id)
        self.profit = self.amount - self.cost
        super().save(**kwargs)
        self.validations_post_save()


class BuyOperation(BaseOperation):
    pass


class BuyItem(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    operation = models.ForeignKey(BuyOperation, on_delete=models.CASCADE)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        return super(BuyItem, self).save()
        # TODO: aqui debo crear el producto si no existe o actualizar el stock si existe


class TransferOperation(BaseOperation):

    def save(self, **kwargs):
        # TODO: In this step I have que made the movement of mony from source account to target account
        return super().save(**kwargs)


class ExtractOperation(BaseOperation):
    period_from = models.DateField()
    period_to = models.DateField()

    def save(self, **kwargs):
        # TODO: In this step I have que made the movement of mony from source account to target account
        return super().save(**kwargs)

