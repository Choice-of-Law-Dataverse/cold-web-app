import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts.col_section import COL_CANDIDATE_AUDIT_PROMPT, COL_RETRIEVAL_QUERY_PROMPT
from ..runner import run_agent
from ..utils import generate_system_prompt
from ..validation import validate_col_candidate_audit
from .document_nav import NAV_TOOLS, DocumentContext
from .hybrid_retrieval import CandidatePassage, RetrievalResult, retrieve_choice_of_law_candidates
from .models import ColCandidateAuditOutput, ColRetrievalQueryPlan, ColSectionOutput, StepResult

logger = logging.getLogger(__name__)

_PLANNER_EXCERPT_CHARS = 6000


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
        generated_queries = await _generate_case_specific_queries(doc_ctx)
        retrieval = await retrieve_choice_of_law_candidates(doc_ctx, generated_queries)
        if not retrieval.candidates:
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
                input=f"{COL_CANDIDATE_AUDIT_PROMPT}\n\nCANDIDATES:\n{_format_candidates(retrieval.candidates, doc_ctx)}",
                context=doc_ctx,
                validate=lambda output, _tools: validate_col_candidate_audit(output, retrieval.candidates),
            )
            output, section_provenance = _assemble_output(audit_step.output, retrieval.candidates, doc_ctx)
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
                    "retrieval": _retrieval_evidence(retrieval),
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
                        for candidate in retrieval.candidates
                    ],
                    "candidate_dispositions": [decision.model_dump() for decision in audit_step.output.decisions],
                    "col_sections": section_provenance,
                },
            )
        except Exception as e:
            logger.error("Error in extract_col_section: %s", e)
            raise
