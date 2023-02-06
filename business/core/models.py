from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .constants import AccountKind


class TimeStampModel(models.Model):
    class Meta:
        abstract = True
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BaseOperation(TimeStampModel):
    amount = models.DecimalField(decimal_places=2)


class SellOperation(BaseOperation):
    @property
    def cost(self):
        # TODO: complete
        pass

    @property
    def profit(self):
        # TODO: complete
        pass


class SellItem(TimeStampModel):
    qty = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    operation = models.ForeignKey(SellOperation, on_delete=models.CASCADE)
    cost = models.DecimalField(decimal_places=2)
    amount = models.DecimalField(decimal_places=2)
    profit = models.DecimalField(decimal_places=2)


class BuyOperation(BaseOperation):
    pass


class BuyItem(TimeStampModel):
    qty = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    operation = models.ForeignKey(BuyOperation, on_delete=models.CASCADE)


class TransferOperation(BaseOperation):
    source_account = models.ForeignKey('Account', on_delete=models.PROTECT)
    target_account = models.ForeignKey('Account', on_delete=models.PROTECT)


class ExtractOperation(BaseOperation):
    period_from = models.DateField()
    period_to = models.DateField()


class Account(TimeStampModel):
    name = models.CharField(max_length=255)
    kind = models.CharField(choices=AccountKind.CHOICES, default=AccountKind.CASH)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    operation = GenericForeignKey('content_type', 'object_id', null=True)
    balance = models.DecimalField(decimal_places=2)


class BaseItem(TimeStampModel):
    code = models.CharField(unique=True)
    title = models.CharField(max_length=255)
    cost = models.DecimalField(decimal_places=2)
    price = models.DecimalField('Precio de venta', decimal_places=2)


class Product(BaseItem):
    pass


class Service(BaseItem):
    pass


class Stock(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.OneToOneField(Product)
