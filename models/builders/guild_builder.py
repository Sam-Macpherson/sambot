from models import Guild
from models.builders.model_builder import ModelBuilder


class GuildBuilder(ModelBuilder):
    model = Guild

    @classmethod
    def build(cls, **kwargs):
        return super().build(**kwargs)
