from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .constants import AccountKind


class TimeStampModel(models.Model):
    class Meta:
        abstract = True
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BaseOperation(TimeStampModel):
    # amount = models.DecimalField(decimal_places=2, max_digits=10)
    target_accounts = models.ManyToManyField('Account')
    source_accounts = models.ManyToManyField('Account')


class SellOperation(BaseOperation):
    @property
    def cost(self):
        return self.sellitem_set.aggregate(models.Sum('cost'))['cost__sum']

    @property
    def profit(self):
        return self.sellitem_set.aggregate(models.Sum('profit'))['profit__sum']

    @property
    def amount(self):
        return self.sellitem_set.aggregate(models.Sum('amount'))['amount__sum']

    def validations(self):
        pass
        # TODO: check available stock of products before save


class SellItem(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    operation = models.ForeignKey(SellOperation, on_delete=models.CASCADE)
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    profit = models.DecimalField(decimal_places=2, max_digits=10)

    def save(self, **kwargs):
        # self.cost = self.qty * self.product_set.aggregate(cost=Sum('cost')).values('cost')
        self.cost = Product.get_total_cost(self.qty, self.product_id)
        self.amount = Product.get_total_price(self.qty, self.product_id)
        self.profit = self.amount - self.cost
        return super().save(**kwargs)


class BuyOperation(BaseOperation):
    pass


class BuyItem(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    operation = models.ForeignKey(BuyOperation, on_delete=models.CASCADE)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        return super(BuyItem, self).save()
        # TODO: aqui debo crear el producto si no existe o actualizar el stock si existe


class TransferOperation(BaseOperation):
    transfer_date = models.DateField()

    def save(self, **kwargs):
        # TODO: In this step I have que made the movement of mony from source account to target account
        return super().save(**kwargs)


class ExtractOperation(BaseOperation):
    period_from = models.DateField()
    period_to = models.DateField()

    def save(self, **kwargs):
        # TODO: In this step I have que made the movement of mony from source account to target account
        return super().save(**kwargs)


class Account(TimeStampModel):
    name = models.CharField(max_length=255)
    kind = models.CharField(choices=AccountKind.CHOICES, default=AccountKind.CASH, max_length=255)
    balance = models.DecimalField(decimal_places=2, max_digits=10)

    def ingress(self):
        pass

    def extract(self):
        # TODO: I need to validate
        pass


class BaseItem(TimeStampModel):
    code = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=255)
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField('Precio de venta', decimal_places=2, max_digits=10)
    enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    @classmethod
    def get_total_cost(cls, qty, item_id):
        return qty * cls.objects.filter(id=item_id).values_list('cost', flat=True)[0]

    @classmethod
    def get_total_price(cls, qty, item_id):
        # TODO: si el producto es una taza, usar hack para retornar precio dinamico
        return qty * cls.objects.filter(id=item_id).values_list('price', flat=True)[0]

    def delete(self, using=None, keep_parents=False):
        self.enabled = False
        self.save()


class Product(BaseItem):
    pass


class Service(BaseItem):
    pass


class Stock(TimeStampModel):
    qty = models.PositiveIntegerField()
    product = models.OneToOneField(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.qty}: {self.product.title}'
