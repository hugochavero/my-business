from django.db import models

__all__ = (
    'Product',
)

from .base import TimeStampModel


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

    def delete(self, **kwargs):
        self.enabled = False
        self.save()


class Product(BaseItem):
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.title} x {self.stock}'


class Service(BaseItem):
    pass
