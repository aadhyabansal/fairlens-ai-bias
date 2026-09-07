from app.engine.text_bias import run_text_bias_test
from app.schemas.text_bias import TextBiasRequest, WordSet


def test_career_family_gender_bias():
    request = TextBiasRequest(
        target_set_a=WordSet(name="career", words=[
            "executive", "management", "professional", "corporation",
            "salary", "office", "business", "career"
        ]),
        target_set_b=WordSet(name="family", words=[
            "home", "parents", "children", "family",
            "cousins", "marriage", "wedding", "relatives"
        ]),
        attribute_set_a=WordSet(name="male", words=[
            "male", "man", "boy", "brother", "he", "him", "his", "son"
        ]),
        attribute_set_b=WordSet(name="female", words=[
            "female", "woman", "girl", "sister", "she", "her", "hers", "daughter"
        ]),
    )

    result = run_text_bias_test(request)

    print(f"\nEffect size: {result.effect_size:.3f}")
    print(f"Interpretation: {result.interpretation}")
    print(f"Warnings: {result.warnings}")

    # This is a well-documented bias in embedding models - expect a real effect
    assert abs(result.effect_size) > 0.2