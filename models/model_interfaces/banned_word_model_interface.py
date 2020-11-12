"""The interface for banned words."""

from models.banned_words import BannedWord
from models.builders.banned_words_builder import BannedWordsBuilder
from models.model_interfaces.model_interface import ModelInterface


class BannedWordModelInterface(ModelInterface):
    model = BannedWord
    builder = BannedWordsBuilder
