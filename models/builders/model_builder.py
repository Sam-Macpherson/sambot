"""A base builder class, for building instances of the given model."""


class ModelBuilder:
    model = None

    @classmethod
    def build(cls, **kwargs):
        record = cls.model.create(**kwargs)
        return record
