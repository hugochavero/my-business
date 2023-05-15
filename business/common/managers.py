from django.db import models

from common.exceptions import NotAllowedAction


class ReadOnlyObjectManager(models.Manager):
    def update(self, *args, **kwargs):
        raise NotAllowedAction

    def delete(self, *args, **kwargs):
        raise NotAllowedAction
