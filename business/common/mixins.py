from typing import List
from django.contrib.admin import ModelAdmin


class ModelAdminMixin:
    @classmethod
    def field_names(cls) -> List[str]:
        """
        This method returns a list of all fields names
        """
        return [f.name for f in cls._meta.fields]

    @classmethod
    def get_admin_class(cls):
        """
        Return a generic ModelAdmin class for the model.
        """
        return type(
            f"{cls.__class__.__name__}Admin",
            (ModelAdmin,),
            dict(list_display=cls.field_names()) or {}
        )
