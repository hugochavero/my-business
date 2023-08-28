from typing import List
from django.contrib.admin import ModelAdmin
from django.db import models

from common.exceptions import NotAllowedAction
from common.managers import ReadOnlyObjectManager


class ModelAdminMixin:
    @classmethod
    def field_names(cls) -> List[str]:
        """
        This method returns a list of all fields names
        """
        return [f.name for f in cls._meta.fields]

    @classmethod
    def get_admin_class(cls, default_model_admin=ModelAdmin):
        """
        Return a generic ModelAdmin class for the model.
        """
        return type(
            f"{cls.__class__.__name__}Admin",
            (default_model_admin,),
            dict(list_display=cls.field_names()) or {},
        )


class ReadOnlyModel(models.Model):
    objects = ReadOnlyObjectManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            return super().save(*args, **kwargs)
        raise NotAllowedAction

    def delete(self, *args, **kwargs):
        raise NotAllowedAction
