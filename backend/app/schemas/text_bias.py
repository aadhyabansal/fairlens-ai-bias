from pydantic import BaseModel, Field

class WordSet(BaseModel):
    name: str
    words: list[str]


class TextBiasRequest(BaseModel):
    target_set_a: WordSet   # e.g. "career" words
    target_set_b: WordSet   # e.g. "family" words
    attribute_set_a: WordSet  # e.g. male-associated terms
    attribute_set_b: WordSet  # e.g. female-associated terms


class TextBiasResult(BaseModel):
    target_set_a_name: str
    target_set_b_name: str
    attribute_set_a_name: str
    attribute_set_b_name: str
    effect_size: float          # WEAT's d-statistic
    interpretation: str         # plain-language severity label
    warnings: list[str] = Field(default_factory=list)