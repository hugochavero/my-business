import inspect
from typing import Callable, Iterable, Dict, Hashable

from django.core.exceptions import ValidationError
from django.db.models import Model


class ValidationModelMixin(Model):
    """
    This class wraps validation, into models from any method that start with a given prefix.
    """

    _validation_members_prefix: str = "_validate_"
    _validation_key: Hashable = "__all__"
    _validations_map: Dict[Hashable, Callable] = None

    class Meta:
        abstract = True

    def clean(self):
        for method in self.get_validation_members():
            method()
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_validation_members(self) -> Iterable[str]:
        """
        Get all the class methods members that follows the name prefix.
        """
        return [
            method[1]
            for method in inspect.getmembers(self, predicate=inspect.ismethod)
            if method[0].startswith(self._validation_members_prefix)
        ]

    @staticmethod
    def _raise_from_condition(condition: bool, error_message: str):
        if condition:
            raise ValidationError(error_message)

    # Validations
    def _validate_map(self):
        """
        Run the given validator in _validations_map using _validation_key as getter.
        """
        if self._validations_map and self._validation_key:
            if self._validation_key == "__all__":
                for _, validator in self._validations_map.items():
                    validator()

            else:
                validator = self._validations_map.get(self._validation_key, None)

                if not validator:
                    raise ValueError(
                        f"{self._validation_key} validator not found in the validators map."
                    )

                if not isinstance(validator, Callable):
                    raise ValueError(
                        f"Validator for {self._validation_key} of type {type(validator)} is not a callable validator."
                    )

                validator()
