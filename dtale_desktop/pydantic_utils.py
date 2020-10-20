from pydantic import BaseModel


def _snake_to_camel(string: str) -> str:
    first_word, *words = string.split("_")
    return f"{first_word}{''.join(word.capitalize() for word in words)}"


class BaseApiModel(BaseModel):
    class Config:
        alias_generator = _snake_to_camel
        allow_population_by_field_name = True

    def json(self, *args, **kwargs):
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().json(*args, **kwargs)

    @classmethod
    def get_by_name_or_alias(cls, values: dict, field_name: str):
        field = cls.__fields__[field_name]
        if field.name in values:
            return values[field_name]
        return values.get(field.alias)
