from models import User
from models.profiles import DiscordProfile
from models.builders.model_builder import ModelBuilder
from models.currencies import Wallet


class UserBuilder(ModelBuilder):
    model = User

    @classmethod
    def build(cls, **kwargs):
        user = super().build(**kwargs)
        Wallet.create(user=user)
        return user
