from models.banned_words import BannedWord
from models.builders.model_builder import ModelBuilder


class BannedWordBuilder(ModelBuilder):
    model = BannedWord

    @classmethod
    def build(cls, **kwargs):
        return super().build(**kwargs)
