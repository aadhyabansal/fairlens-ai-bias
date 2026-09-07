import numpy as np
from sentence_transformers import SentenceTransformer

from app.schemas.text_bias import TextBiasRequest, TextBiasResult

_model = None  # loaded once, reused across calls — loading is expensive


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _mean_cosine_similarity(word_vec: np.ndarray, attribute_vecs: np.ndarray) -> float:
    """Average cosine similarity between one word and a set of attribute words."""
    sims = [_cosine_similarity(word_vec, av) for av in attribute_vecs]
    return float(np.mean(sims))


def _association(word_vec: np.ndarray, attr_a_vecs: np.ndarray, attr_b_vecs: np.ndarray) -> float:
    """
    WEAT's core association measure for a single word:
    how much more similar is this word to attribute set A than to attribute set B.
    """
    return _mean_cosine_similarity(word_vec, attr_a_vecs) - _mean_cosine_similarity(word_vec, attr_b_vecs)


def _interpret_effect_size(d: float) -> str:
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible association bias"
    elif abs_d < 0.5:
        return "small association bias"
    elif abs_d < 0.8:
        return "moderate association bias"
    else:
        return "large association bias"


def run_text_bias_test(request: TextBiasRequest) -> TextBiasResult:
    warnings = []

    for ws in [request.target_set_a, request.target_set_b, request.attribute_set_a, request.attribute_set_b]:
        if len(ws.words) < 5:
            warnings.append(
                f"Word set '{ws.name}' has only {len(ws.words)} words — "
                f"WEAT results are more reliable with 8+ words per set."
            )

    model = _get_model()

    target_a_vecs = model.encode(request.target_set_a.words)
    target_b_vecs = model.encode(request.target_set_b.words)
    attr_a_vecs = model.encode(request.attribute_set_a.words)
    attr_b_vecs = model.encode(request.attribute_set_b.words)

    # Association score for every word in each target set
    assoc_a = [_association(w, attr_a_vecs, attr_b_vecs) for w in target_a_vecs]
    assoc_b = [_association(w, attr_a_vecs, attr_b_vecs) for w in target_b_vecs]

    # WEAT effect size: standardized difference in mean association
    # between the two target sets, pooled by the combined standard deviation
    mean_diff = np.mean(assoc_a) - np.mean(assoc_b)
    pooled_std = np.std(assoc_a + assoc_b, ddof=1)

    effect_size = float(mean_diff / pooled_std) if pooled_std > 0 else 0.0

    return TextBiasResult(
        target_set_a_name=request.target_set_a.name,
        target_set_b_name=request.target_set_b.name,
        attribute_set_a_name=request.attribute_set_a.name,
        attribute_set_b_name=request.attribute_set_b.name,
        effect_size=effect_size,
        interpretation=_interpret_effect_size(effect_size),
        warnings=warnings,
    )