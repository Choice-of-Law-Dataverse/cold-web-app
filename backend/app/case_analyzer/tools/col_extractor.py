import asyncio
import logging
from collections.abc import Sequence

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..jev import JEV_STATE_MAX_CHARS, NoulAnswer, ask_jev, noul_question
from ..prompts.col_section import COL_CANDIDATE_AUDIT_PROMPT, COL_RETRIEVAL_QUERY_PROMPT
from ..runner import run_agent
from ..utils import generate_system_prompt
from ..validation import validate_col_candidate_audit
from .document_nav import NAV_TOOLS, DocumentContext
from .hybrid_retrieval import (
    DEFAULT_MAX_CANDIDATE_CHARS,
    DEFAULT_MAX_CANDIDATES,
    MAX_MERGED_PARAGRAPHS,
    CandidatePassage,
    RetrievalResult,
    retrieve_choice_of_law_candidates,
)
from .models import ColCandidateAuditOutput, ColRetrievalQueryPlan, ColSectionOutput, StepResult

logger = logging.getLogger(__name__)

_PLANNER_EXCERPT_CHARS = 6000
_JEV_PARAGRAPH_CONCURRENCY = 16
_JEV_PRUNING_TIMEOUT_SECONDS = 8.0
JEV_PARAGRAPH_THRESHOLD = 0.3
"""Paragraphs Jev rates at or above this are offered to the audit; at 0.3 they kept ~95% of the recoverable
curated excerpt from 38-51% of the text in the analyzer evals."""

COL_PARAGRAPH_QUESTION = noul_question(
    {
        "question": "Is this paragraph part of the court's own choice-of-law analysis?",
        "focus": "The court's determination of which law governs the dispute, and its reasoning for it.",
    },
    true={
        "what": "The court states, applies or reasons about which law governs: a choice-of-law clause or agreement, "
        "a conflict-of-laws rule, connecting factors, or an exception such as public policy or overriding "
        "mandatory rules.",
        "examples": [
            "The parties validly chose Swiss law.",
            "Absent a choice, the contract is governed by the law of the seller's habitual residence.",
        ],
    },
    false={
        "what": "Facts, procedure, the court's own jurisdiction, costs, the merits decided under the governing law, "
        "or a party's argument the court does not adopt.",
    },
)


def _responses_model(task: str) -> OpenAIResponsesModel:
    return OpenAIResponsesModel(model=get_model(task), openai_client=get_openai_client())


async def _generate_case_specific_queries(doc_ctx: DocumentContext) -> list[str]:
    headings = "\n".join(heading for heading, _index in doc_ctx.headings[:30]) or "[no headings detected]"
    planner_input = (
        f"{COL_RETRIEVAL_QUERY_PROMPT}\n\n"
        f"DOCUMENT HEADINGS:\n{headings}\n\n"
        f"DOCUMENT EXCERPT:\n{doc_ctx.text[:_PLANNER_EXCERPT_CHARS]}"
    )
    planner = Agent[None](
        name="ColRetrievalQueryPlanner",
        instructions=generate_system_prompt(),
        output_type=ColRetrievalQueryPlan,
        model=_responses_model("col_retrieval"),
    )
    try:
        result = await Runner.run(planner, input=planner_input)
    except Exception as exc:
        logger.warning("Case-specific retrieval query planning failed: %s", type(exc).__name__)
        return []
    return list(dict.fromkeys(query.strip() for query in result.final_output.queries if query.strip()))[:6]


async def jev_paragraph_probabilities(paragraphs: Sequence[str], timeout: float | None = None) -> list[float | None]:
    """Jev's probability that each paragraph belongs to the court's choice-of-law analysis.

    None where Jev gave no answer, including every paragraph still unanswered when the timeout passes.
    """
    semaphore = asyncio.Semaphore(_JEV_PARAGRAPH_CONCURRENCY)

    async def ask(paragraph: str) -> float | None:
        async with semaphore:
            response = await ask_jev("col_paragraph", paragraph[:JEV_STATE_MAX_CHARS], {"relevant": COL_PARAGRAPH_QUESTION})
        answer = response.answers.get("relevant") if response else None
        return answer.noul if isinstance(answer, NoulAnswer) else None

    tasks = [asyncio.create_task(ask(paragraph)) for paragraph in paragraphs]
    if not tasks:
        return []
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    for task in pending:
        task.cancel()
    if pending:
        logger.warning("Jev answered %d of %d paragraphs before the timeout", len(done), len(tasks))
    return [task.result() if task in done else None for task in tasks]


def jev_candidates(
    doc_ctx: DocumentContext,
    probabilities: Sequence[float | None],
    threshold: float = JEV_PARAGRAPH_THRESHOLD,
) -> list[CandidatePassage]:
    """Runs of consecutive paragraphs Jev rates relevant, within the audit's candidate and size limits.

    A paragraph Jev gave no answer for is kept, ranked with the least relevant, so a failed or late request
    never hides text from the audit but never crowds out paragraphs Jev rated relevant either.
    """
    runs: list[tuple[int, int, float]] = []
    for number, probability in enumerate(probabilities, start=1):
        if probability is not None and probability < threshold:
            continue
        score = threshold if probability is None else probability
        if runs and runs[-1][1] == number - 1 and number - runs[-1][0] < MAX_MERGED_PARAGRAPHS:
            start, _end, best = runs[-1]
            runs[-1] = (start, number, max(best, score))
        else:
            runs.append((number, number, score))

    selected: list[tuple[int, int, float]] = []
    selected_chars = 0
    for start, end, score in sorted(runs, key=lambda run: (-run[2], run[0])):
        run_chars = sum(len(paragraph) for paragraph in doc_ctx.paragraphs[start - 1 : end])
        if selected and selected_chars + run_chars > DEFAULT_MAX_CANDIDATE_CHARS:
            continue
        selected.append((start, end, score))
        selected_chars += run_chars
        if len(selected) == DEFAULT_MAX_CANDIDATES:
            break
    return [
        CandidatePassage(
            candidate_id=f"C{index:03d}",
            start_paragraph=start,
            end_paragraph=end,
            text="\n\n".join(doc_ctx.paragraphs[start - 1 : end]),
            concepts=("jev_relevance",),
            retrieval_methods=("jev",),
            reciprocal_rank_score=score,
        )
        for index, (start, end, score) in enumerate(sorted(selected), start=1)
    ]


async def _retrieve_with_jev(doc_ctx: DocumentContext) -> list[CandidatePassage]:
    """Jev-selected candidates, or none when Jev is unavailable, answers nothing in time, or finds nothing relevant."""
    probabilities = await jev_paragraph_probabilities(doc_ctx.paragraphs, timeout=_JEV_PRUNING_TIMEOUT_SECONDS)
    if all(probability is None for probability in probabilities):
        return []
    return jev_candidates(doc_ctx, probabilities)


def _format_candidates(candidates: list[CandidatePassage], doc_ctx: DocumentContext) -> str:
    rendered: list[str] = []
    for candidate in candidates:
        header = (
            f"[{candidate.candidate_id}: paragraphs {candidate.start_paragraph}-{candidate.end_paragraph}; "
            f"methods={','.join(candidate.retrieval_methods)}; concepts={','.join(candidate.concepts)}]"
        )
        body = "\n\n".join(f"[paragraph {number}]\n{doc_ctx.paragraphs[number - 1]}" for number in candidate.paragraph_numbers)
        rendered.append(f"{header}\n{body}")
    return "\n\n---\n\n".join(rendered)


def _assemble_output(
    audit: ColCandidateAuditOutput,
    candidates: list[CandidatePassage],
    doc_ctx: DocumentContext,
) -> tuple[ColSectionOutput, list[dict[str, object]]]:
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    sections: list[str] = []
    provenance: list[dict[str, object]] = []
    section_by_paragraphs: dict[tuple[int, ...], int] = {}
    for decision in audit.decisions:
        if decision.disposition != "include" or decision.role is None:
            continue
        paragraph_numbers = tuple(sorted(decision.selected_paragraphs))
        candidate = candidate_by_id[decision.candidate_id]
        existing_index = section_by_paragraphs.get(paragraph_numbers)
        if existing_index is not None:
            existing = provenance[existing_index]
            candidate_ids = existing["candidate_ids"]
            retrieval_methods = existing["retrieval_methods"]
            if isinstance(candidate_ids, list):
                candidate_ids.append(decision.candidate_id)
            if isinstance(retrieval_methods, list):
                existing["retrieval_methods"] = sorted(set(retrieval_methods) | set(candidate.retrieval_methods))
            if decision.role in {"court_holding", "court_reasoning"}:
                existing["role"] = decision.role
            continue
        section_by_paragraphs[paragraph_numbers] = len(sections)
        sections.append("\n\n".join(doc_ctx.paragraphs[number - 1] for number in paragraph_numbers))
        provenance.append(
            {
                "section_index": len(sections) - 1,
                "paragraphs": list(paragraph_numbers),
                "role": decision.role,
                "candidate_ids": [decision.candidate_id],
                "retrieval_methods": list(candidate.retrieval_methods),
            }
        )
    return (
        ColSectionOutput(col_sections=sections, confidence=audit.confidence, reasoning=audit.reasoning),
        provenance,
    )


def _retrieval_evidence(retrieval: RetrievalResult) -> dict[str, object]:
    return {
        "query_count": retrieval.query_count,
        "semantic_available": retrieval.semantic_available,
        "semantic_unavailable_reason": retrieval.semantic_unavailable_reason,
        "semantic_embedding_tokens": retrieval.semantic_embedding_tokens,
        "semantic_chunk_count": retrieval.semantic_chunk_count,
        "lexical_hit_count": retrieval.lexical_hit_count,
        "semantic_hit_count": retrieval.semantic_hit_count,
        "lexical_semantic_overlap": retrieval.overlap_count,
        "lexical_fallback": not retrieval.semantic_available,
    }


async def extract_col_section(
    doc_ctx: DocumentContext,
) -> StepResult[ColSectionOutput]:
    with logfire.span("col_section"):
        candidates = await _retrieve_with_jev(doc_ctx)
        if candidates:
            retrieval_evidence: dict[str, object] = {
                "method": "jev",
                "threshold": JEV_PARAGRAPH_THRESHOLD,
                "candidate_paragraph_count": sum(len(c.paragraph_numbers) for c in candidates),
            }
        else:
            generated_queries = await _generate_case_specific_queries(doc_ctx)
            retrieval = await retrieve_choice_of_law_candidates(doc_ctx, generated_queries)
            candidates = retrieval.candidates
            retrieval_evidence = {"method": "hybrid", **_retrieval_evidence(retrieval)}
        if not candidates:
            raise ValueError("No choice-of-law retrieval candidates were found")

        agent = Agent[DocumentContext](
            name="ColSectionExtractor",
            instructions=generate_system_prompt(),
            output_type=ColCandidateAuditOutput,
            tools=NAV_TOOLS,
            model=_responses_model("col_section"),
        )

        try:
            audit_step = await run_agent(
                agent,
                input=f"{COL_CANDIDATE_AUDIT_PROMPT}\n\nCANDIDATES:\n{_format_candidates(candidates, doc_ctx)}",
                context=doc_ctx,
                validate=lambda output, _tools: validate_col_candidate_audit(output, candidates),
            )
            output, section_provenance = _assemble_output(audit_step.output, candidates, doc_ctx)
            included_paragraphs: list[int] = []
            for section in section_provenance:
                paragraph_numbers = section.get("paragraphs")
                if isinstance(paragraph_numbers, list):
                    included_paragraphs.extend(number for number in paragraph_numbers if isinstance(number, int))
            rejected_candidate_ids = [
                decision.candidate_id for decision in audit_step.output.decisions if decision.disposition == "exclude"
            ]
            logfire.info(
                "Choice-of-law candidates audited",
                selected_paragraph_ids=sorted(set(included_paragraphs)),
                rejected_candidate_ids=rejected_candidate_ids,
            )
            return StepResult(
                output=output,
                response_id=audit_step.response_id,
                tool_names=audit_step.tool_names,
                evidence={
                    "retrieval": retrieval_evidence,
                    "candidates": [
                        {
                            "candidate_id": candidate.candidate_id,
                            "start_paragraph": candidate.start_paragraph,
                            "end_paragraph": candidate.end_paragraph,
                            "concepts": list(candidate.concepts),
                            "retrieval_methods": list(candidate.retrieval_methods),
                            "reciprocal_rank_score": candidate.reciprocal_rank_score,
                            "semantic_score": candidate.semantic_score,
                        }
                        for candidate in candidates
                    ],
                    "candidate_dispositions": [decision.model_dump() for decision in audit_step.output.decisions],
                    "col_sections": section_provenance,
                },
            )
        except Exception as e:
            logger.error("Error in extract_col_section: %s", e)
            raise
