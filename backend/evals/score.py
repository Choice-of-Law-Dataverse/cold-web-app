"""Score analyzer step outputs against curated values.

Deterministic where the curated value allows it; free-text steps are judged by Jev, which
answers "does the candidate convey the reference's legal substance?" with a probability.
"""

import re
from typing import Any

from rapidfuzz import fuzz

from app.case_analyzer.jev import NoulAnswer, ask_jev, noul_question

from .budget import Budget

MATCH_SCORE = 80
JUDGE_QUESTION = noul_question(
    "Does the candidate answer convey the same legal substance as the reference answer "
    "(same court, law, rule, reasoning and outcome), even if worded differently or shorter?",
    true="The candidate agrees with the reference on every legally material point.",
    false="The candidate omits, contradicts or misstates a legally material point of the reference.",
)


def excerpt_recall(sections: list[str], excerpt: str) -> float:
    """How much of the curated excerpt the extracted sections contain, from 0 to 1.

    partial_ratio aligns the shorter text inside the longer one, so a few words copied from a long excerpt would
    match it perfectly; the score is capped at the extracted text's share of the excerpt's length (both normalized),
    since the sections cannot cover more of the excerpt than they hold.
    """
    extracted, reference = normalize(" ".join(sections)), normalize(excerpt)
    if not extracted or not reference:
        return 0.0
    return min(fuzz.partial_ratio(reference, extracted) / 100, len(extracted) / len(reference))


def identifier_match(identifier: str, reference: str) -> float:
    """Whether the curated citation contains the identifier's numbers as a consecutive run, whatever language or court
    naming either side uses.

    Numbers are compared whole, so 12 does not match 312 and 1/23 does not match 12/3.
    """
    numbers = re.findall(r"\d+", identifier)
    reference_numbers = re.findall(r"\d+", reference)
    return float(
        bool(numbers)
        and any(
            reference_numbers[start : start + len(numbers)] == numbers
            for start in range(len(reference_numbers) - len(numbers) + 1)
        )
    )


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


async def judge(candidate: str, reference: str, budget: Budget | None = None) -> dict[str, float]:
    """Jev's agreement between the candidate and the reference.

    Each judgement is a paid Jev call made by the evaluator, outside the case's task, so it is never in a case's cost
    and is asked again on every run, cached or not. With a budget it is not asked once the budget is spent (raising
    BudgetExceeded, which leaves the case unscored), and what OpenRouter reports for it is added to judge_spent.
    """
    if budget is not None:
        budget.check()
    response = await ask_jev("eval_judge", {"reference": reference, "candidate": candidate}, {"agrees": JUDGE_QUESTION})
    if budget is not None and response is not None:
        budget.add_judge_cost(response.usage.cost)
    answer = response.answers.get("agrees") if response else None
    if not isinstance(answer, NoulAnswer):
        return {}
    return {"agreement": answer.noul, "agrees": float(answer.noul >= 0.5)}


async def score(step: str, output: dict[str, Any], gold: dict[str, Any], budget: Budget | None = None) -> dict[str, float]:
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
            return {
                "match": float(bool(predicted) and fuzz.token_set_ratio(predicted, reference) >= 90),
                "identifier_match": identifier_match(output.get("identifier") or output.get("case_citation", ""), reference),
                "has_year": float(bool(re.search(r"\b(1[89]|20)\d\d\b", predicted))),
            }
        case "relevant_facts" | "col_issue" | "courts_position" | "abstract":
            return await judge(str(output.get(step, "")), gold[step], budget)
    raise ValueError(f"No scorer for step {step}")
