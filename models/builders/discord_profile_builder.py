from models.builders.model_builder import ModelBuilder
from models.builders.user_builder import UserBuilder
from models.profiles import DiscordProfile


class DiscordProfileBuilder(ModelBuilder):
    model = DiscordProfile

    @classmethod
    def build(cls, **kwargs):
        user = UserBuilder.build()
        profile = super().build(user=user, **kwargs)
        return profile
