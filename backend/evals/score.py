"""Score analyzer step outputs against curated values.

Deterministic where the curated value allows it; free-text steps are judged by Jev, which
answers "does the candidate convey the reference's legal substance?" with a probability.
"""

import re
from typing import Any

from rapidfuzz import fuzz

from app.case_analyzer.jev import NoulAnswer, ask_jev, noul_question

MATCH_SCORE = 80
JUDGE_QUESTION = noul_question(
    "Does the candidate answer convey the same legal substance as the reference answer "
    "(same court, law, rule, reasoning and outcome), even if worded differently or shorter?",
    true="The candidate agrees with the reference on every legally material point.",
    false="The candidate omits, contradicts or misstates a legally material point of the reference.",
)


def excerpt_recall(sections: list[str], excerpt: str) -> float:
    """How much of the curated excerpt the extracted sections contain, from 0 to 1."""
    extracted = normalize(" ".join(sections))
    return fuzz.partial_ratio(normalize(excerpt), extracted) / 100 if extracted else 0.0


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold().strip()


def set_scores(predicted: list[str], gold: list[str], exact: bool = False) -> dict[str, float]:
    """Precision/recall/F1, matching items exactly or by fuzzy token overlap.

    Provisions and citations differ mainly in their numbers, so fuzzy matches also need identical numbers.
    """

    def matches(a: str, b: str) -> bool:
        if exact:
            return a == b
        numbers_agree = re.findall(r"\d+", a) == re.findall(r"\d+", b)
        return numbers_agree and fuzz.token_set_ratio(normalize(a), normalize(b)) >= MATCH_SCORE

    true_positives = sum(1 for p in predicted if any(matches(p, g) for g in gold))
    found = sum(1 for g in gold if any(matches(p, g) for p in predicted))
    precision = true_positives / len(predicted) if predicted else float(not gold)
    recall = found / len(gold) if gold else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


async def judge(candidate: str, reference: str) -> dict[str, float]:
    response = await ask_jev("eval_judge", {"reference": reference, "candidate": candidate}, {"agrees": JUDGE_QUESTION})
    answer = response.answers.get("agrees") if response else None
    if not isinstance(answer, NoulAnswer):
        return {}
    return {"agreement": answer.noul, "agrees": float(answer.noul >= 0.5)}


async def score(step: str, output: dict[str, Any], gold: dict[str, Any]) -> dict[str, float]:
    match step:
        case "jurisdiction":
            curated = gold.get("jurisdiction_codes") or [gold["jurisdiction_code"].upper()]
            return {"accuracy": float(output.get("jurisdiction_code", "").upper() in curated)}
        case "col_section":
            sections = output.get("col_sections", [])
            excerpt = normalize(gold["col_excerpt"])
            return {
                "excerpt_recall": excerpt_recall(sections, gold["col_excerpt"]),
                "length_ratio": len(normalize(" ".join(sections))) / len(excerpt) if excerpt else 0.0,
            }
        case "themes":
            predicted = [t for t in output.get("themes", []) if t != "NA"]
            return set_scores(predicted, gold["themes"], exact=True) | {"exact": float(set(predicted) == set(gold["themes"]))}
        case "pil_provisions":
            return set_scores(output.get("pil_provisions", []), gold["pil_provisions"])
        case "case_citation":
            predicted, reference = normalize(output.get("case_citation", "")), normalize(gold["case_citation"])
            return {"match": float(bool(predicted) and fuzz.token_set_ratio(predicted, reference) >= 90)}
        case "relevant_facts" | "col_issue" | "courts_position" | "abstract":
            return await judge(str(output.get(step, "")), gold[step])
    raise ValueError(f"No scorer for step {step}")
