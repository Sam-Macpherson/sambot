from models.builders.model_builder import ModelBuilder
from models.triggered_responses import TriggeredResponse


class TriggeredResponseBuilder(ModelBuilder):
    model = TriggeredResponse

    @classmethod
    def build(cls, **kwargs):
        return super().build(**kwargs)
