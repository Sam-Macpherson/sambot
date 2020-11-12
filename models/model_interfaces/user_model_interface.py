"""The interface for users."""

from models import User
from models.builders import UserBuilder
from models.model_interfaces.model_interface import ModelInterface


class UserModelInterface(ModelInterface):
    model = User
    builder = UserBuilder
