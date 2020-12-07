"""Class to interface with the Currency model."""
from models.builders import CurrencyBuilder
from models.currencies import Currency
from models.model_interfaces import ModelInterface


class CurrencyModelInterface(ModelInterface):
    model = Currency
    builder = CurrencyBuilder

    @classmethod
    def get_or_create(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_or_none(cls, **kwargs):
        raise NotImplementedError
