import re
import json
from app.schemas.report import ReportRequest, ReportResult, ReportFinding
from app.engine.llm_provider import GeminiProvider, LLMProvider

_provider = None

def _get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = GeminiProvider()
    return _provider

def _extract_numbers(obj, found: set[float]) -> None:
    """
    Recursively walks a JSON-like structure (dict/list/values) and collects
    every numeric value it finds, rounded to 2 decimal places for comparison.
    This becomes our "ground truth" set of real numbers Gemini is allowed to cite.
    """
    if isinstance(obj, dict):
        for v in obj.values():
            _extract_numbers(v, found)
    elif isinstance(obj, list):
        for v in obj:
            _extract_numbers(v, found)
    elif isinstance(obj, (int, float)):
        found.add(round(float(obj), 2))


def _extract_numbers_from_text(text: str) -> set[float]:
    """Pulls out every number-like token mentioned in a piece of text."""
    matches = re.findall(r"-?\d+\.?\d*", text)
    numbers = set()
    for m in matches:
        try:
            numbers.add(round(float(m), 2))
        except ValueError:
            continue
    return numbers


def _build_prompt(audit_json: dict, context: str) -> str:
    return f"""You are a fairness audit report generator. You will be given
structured JSON output from a bias detection engine. Your job is to explain
the findings in plain language, grounded STRICTLY in the numbers provided.

CRITICAL RULES:
1. Every finding must cite a specific number from the JSON (in the "cited_metric" field).
2. NEVER invent a number, percentage, or statistic that is not in the JSON.
3. Recommendations must reference the specific metric or feature that motivated them —
   no generic advice like "collect more diverse data" without tying it to a specific
   number from this audit.
4. If the JSON shows no meaningful disparity, say so plainly. Do not manufacture
   a finding to fill space.

Context: {context if context else "No additional context provided."}

Audit JSON:
{json.dumps(audit_json, indent=2)}

Respond with ONLY valid JSON matching this exact structure, no markdown fences,
no preamble:
{{
  "summary": "2-3 sentence plain-language overview",
  "findings": [
    {{
      "title": "short finding title",
      "explanation": "plain-language explanation with real-world harm framing",
      "cited_metric": "the exact number/field from the JSON this is based on",
      "severity": "low|moderate|high|critical",
      "recommendation": "specific action tied to the cited metric or feature"
    }}
  ]
}}"""


def _validate_findings(findings: list[dict], source_json: dict) -> tuple[bool, list[str]]:
    """
    Soft validation: for each finding, check that at least one number mentioned
    in its cited_metric or explanation is actually present in the source JSON
    (within rounding tolerance). Flags findings that don't, but doesn't block
    the whole report on one weak finding.
    """
    source_numbers = set()
    _extract_numbers(source_json, source_numbers)

    notes = []
    all_valid = True

    for i, finding in enumerate(findings):
        text_to_check = f"{finding.get('cited_metric', '')} {finding.get('explanation', '')}"
        cited_numbers = _extract_numbers_from_text(text_to_check)

        # Check if any cited number is close to a real number in the source
        # (tolerance of 0.02 to allow for minor rounding differences)
        grounded = any(
            any(abs(cited - real) < 0.02 for real in source_numbers)
            for cited in cited_numbers
        )

        if not cited_numbers:
            notes.append(f"Finding {i+1} ('{finding.get('title', '?')}') cites no numeric value at all.")
            all_valid = False
        elif not grounded:
            notes.append(
                f"Finding {i+1} ('{finding.get('title', '?')}') cites numbers "
                f"not found in the source data: {cited_numbers}"
            )
            all_valid = False

    return all_valid, notes

def generate_report(request: ReportRequest) -> ReportResult:
    provider = _get_provider()
    prompt = _build_prompt(request.audit_json, request.context)

    try:
        raw_text = provider.generate(prompt)
    except Exception as e:
        # LLM layer is fully unavailable — degrade gracefully, don't fail the audit.
        return ReportResult(
            summary="Narrative report unavailable — the AI reporting service could not be reached. "
                    "Raw fairness metrics remain valid and are unaffected.",
            findings=[],
            validation_passed=False,
            validation_notes=[f"LLM generation failed after all retries/fallbacks: {e}"],
        )

    raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        return ReportResult(
            summary="Narrative report unavailable — the AI response could not be parsed. "
                    "Raw fairness metrics remain valid and are unaffected.",
            findings=[],
            validation_passed=False,
            validation_notes=[f"Failed to parse LLM output as JSON: {e}"],
        )

    findings_data = parsed.get("findings", [])
    is_valid, validation_notes = _validate_findings(findings_data, request.audit_json)
    findings = [ReportFinding(**f) for f in findings_data]

    return ReportResult(
        summary=parsed.get("summary", ""),
        findings=findings,
        validation_passed=is_valid,
        validation_notes=validation_notes,
    )
