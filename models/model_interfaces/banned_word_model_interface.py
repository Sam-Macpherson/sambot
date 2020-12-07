"""Class to interface with the BannedWord model."""
from models.banned_words import BannedWord
from models.builders import BannedWordBuilder
from models.model_interfaces import ModelInterface


class BannedWordModelInterface(ModelInterface):
    model = BannedWord
    builder = BannedWordBuilder

    @staticmethod
    def _hash_word(word):
        from hashlib import sha256
        return sha256(word.encode()).hexdigest()

    @classmethod
    def get_or_none(cls, word=None, **kwargs):
        return super().get_or_none(word=cls._hash_word(word), **kwargs)

    @classmethod
    def get_or_create(cls, word=None, **kwargs):
        return super().get_or_create(word=cls._hash_word(word), **kwargs)
