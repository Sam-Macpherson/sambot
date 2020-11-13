from models.builders.model_builder import ModelBuilder
from models.currencies import Currency


class CurrencyBuilder(ModelBuilder):
    model = Currency

    @classmethod
    def build(cls, **kwargs):
        return super().build(**kwargs)
