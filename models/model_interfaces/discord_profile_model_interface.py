"""Class to interface with the DiscordProfile model."""
from models.builders import DiscordProfileBuilder
from models.model_interfaces import ModelInterface
from models.profiles import DiscordProfile


class DiscordProfileModelInterface(ModelInterface):
    model = DiscordProfile
    builder = DiscordProfileBuilder
