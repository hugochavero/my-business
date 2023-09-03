from django.db import models

__all__ = ("Product",)

from common.mixins import ModelAdminMixin
from .base import TimeStampModel


class BaseItem(TimeStampModel, ModelAdminMixin):
    code = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=255)
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField("Precio de venta", decimal_places=2, max_digits=10)
    enabled = models.BooleanField(default=True)
    last_price_date = models.DateField("Ultima actualizacion precio", null=True)

    class Meta:
        abstract = True
        ordering = ("title",)

    def __str__(self):
        return self.title

    @classmethod
    def get_total_cost(cls, qty, item_id):
        return qty * cls.objects.get(id=item_id).cost

    @classmethod
    def get_total_price(cls, qty, item_id):
        # TODO: si el producto es una taza, usar hack para retornar precio dinamico
        obj = cls.objects.get(id=item_id)
        if obj.code == "TRC01":
            if qty < 12:
                return qty * obj.price
            elif 12 <= qty < 36:
                return qty * 995
            else:
                return qty * 950
        return qty * obj.price

    def delete(self, **kwargs):
        self.enabled = False
        self.save()


class Product(BaseItem):
    stock = models.PositiveIntegerField()
    external_code = models.CharField(max_length=255, blank=True)
    box_size = models.PositiveIntegerField("Unidades por Caja", null=True)

    def __str__(self):
        return f"{self.title} x {self.stock}"

    @property
    def stock_in_boxes(self):
        if self.box_size:
            return int(self.stock / self.box_size)

    def increase_stock(self, qty):
        self.stock += qty
        self.save()

    def decrease_stock(self, qty):
        self.stock -= qty
        self.save()


class Service(TimeStampModel, ModelAdminMixin):
    code = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=255)
