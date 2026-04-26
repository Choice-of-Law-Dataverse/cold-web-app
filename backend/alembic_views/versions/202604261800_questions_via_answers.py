"""Derive every Question relation through Answers / HCCH Answers (no direct M2M).

The Answer entity is JURISDICTION + QUESTION + {ANSWER}; everything else
(Court Decisions, Literature, Instruments, Legal Provisions, ...) attaches to
an Answer rather than directly to a Question. This migration aligns the
`get_entity_detail` view with that model so the direct
`_nc_m2m_Questions_<Entity>` link tables in NocoDB can be dropped safely.

Patched blocks (all in `data_views.get_entity_detail`):

Forward — `'questions'` relation on each entity:
  - Court Decisions ............ via `_nc_m2m_Answers_Court_Decisions`
  - Domestic Instruments ....... via `_nc_m2m_Answers_Domestic_Instru`
  - Domestic Legal Provisions .. via `_nc_m2m_Answers_Domestic_Legal_` + `_1`
  - Regional Legal Provisions .. via `_nc_m2m_HCCH_Answers_Regional_Legal_`
  - International Legal Provisions  via `_nc_m2m_HCCH_Answers_International_L`

Reverse — relations exposed on the `Questions` branch (now derived through
the answer hubs instead of the direct Q↔Entity tables):
  - court_decisions, domestic_instruments, domestic_legal_provisions,
    regional_legal_provisions, international_legal_provisions

Themes — on the Court Decisions branch, themes were derived as
`Themes ← Questions ← Court_Decisions`; rewritten as
`Themes ← Questions ← Answers ← Court_Decisions`.

Every other branch is preserved by sourcing the prior migration's
DETAIL_FUNCTION verbatim and applying explicit string substitutions; each
substitution must hit exactly once, otherwise the migration fails loudly.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from alembic import op

revision = "202604261800"
down_revision = "202604251200"
branch_labels = None
depends_on = None

PRIOR_REVISION_FILENAME = "202604251000_sort_chronological_relations.py"


def _load_prior_module() -> Any:
    prior_path = Path(__file__).parent / PRIOR_REVISION_FILENAME
    spec = importlib.util.spec_from_file_location("_cold_prior_view_chronological", prior_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load prior migration at {prior_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PATCHES: list[tuple[str, str]] = [
    (
        """            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*) ORDER BY data_views._sortable_date(r.date) DESC NULLS LAST)
                FROM data_views.rel_court_decisions r
                JOIN {S}."_nc_m2m_Questions_Court_Decisions" m ON m."Court_Decisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),""",
        """            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*) ORDER BY data_views._sortable_date(r.date) DESC NULLS LAST)
                FROM data_views.rel_court_decisions r
                WHERE r.id IN (
                    SELECT acd."Court_Decisions_id"
                    FROM {S}."_nc_m2m_Answers_Court_Decisions" acd
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = acd."Answers_id"
                    WHERE qa."Questions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'domestic_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_instruments r
                JOIN {S}."_nc_m2m_Questions_Domestic_Instru" m ON m."Domestic_Instruments_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),""",
        """            'domestic_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_instruments r
                WHERE r.id IN (
                    SELECT adi."Domestic_Instruments_id"
                    FROM {S}."_nc_m2m_Answers_Domestic_Instru" adi
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = adi."Answers_id"
                    WHERE qa."Questions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                JOIN {S}."_nc_m2m_Questions_Domestic_Legal_" m ON m."Domestic_Legal_Provisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),""",
        """            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                WHERE r.id IN (
                    SELECT adl."Domestic_Legal_Provisions_id"
                    FROM {S}."_nc_m2m_Answers_Domestic_Legal_" adl
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = adl."Answers_id"
                    WHERE qa."Questions_id" = v_id
                    UNION
                    SELECT adl1."Domestic_Legal_Provisions_id"
                    FROM {S}."_nc_m2m_Answers_Domestic_Legal_1" adl1
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = adl1."Answers_id"
                    WHERE qa."Questions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'international_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_legal_provisions r
                JOIN {S}."_nc_m2m_Questions_International_L" m ON m."International_Legal_Provisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),""",
        """            'international_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_legal_provisions r
                WHERE r.id IN (
                    SELECT hil."International_Legal_Provisions_id"
                    FROM {S}."_nc_m2m_HCCH_Answers_International_L" hil
                    JOIN {S}."_nc_m2m_Questions_HCCH_Answers" qa ON qa."HCCH_Answers_id" = hil."HCCH_Answers_id"
                    WHERE qa."Questions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'regional_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_legal_provisions r
                JOIN {S}."_nc_m2m_Questions_Regional_Legal_" m ON m."Regional_Legal_Provisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),""",
        """            'regional_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_legal_provisions r
                WHERE r.id IN (
                    SELECT hrl."Regional_Legal_Provisions_id"
                    FROM {S}."_nc_m2m_HCCH_Answers_Regional_Legal_" hrl
                    JOIN {S}."_nc_m2m_Questions_HCCH_Answers" qa ON qa."HCCH_Answers_id" = hrl."HCCH_Answers_id"
                    WHERE qa."Questions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Court_Decisions" m ON m."Questions_id" = r.id
                WHERE m."Court_Decisions_id" = v_id
            ), '[]'::jsonb),""",
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                WHERE r.id IN (
                    SELECT qa."Questions_id"
                    FROM {S}."_nc_m2m_Answers_Court_Decisions" acd
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = acd."Answers_id"
                    WHERE acd."Court_Decisions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'themes', COALESCE((
                SELECT jsonb_agg(DISTINCT to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Questions" tq ON tq."Themes_id" = r.id
                JOIN {S}."_nc_m2m_Questions_Court_Decisions" qcd ON qcd."Questions_id" = tq."Questions_id"
                WHERE qcd."Court_Decisions_id" = v_id
            ), '[]'::jsonb),""",
        """            'themes', COALESCE((
                SELECT jsonb_agg(DISTINCT to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Questions" tq ON tq."Themes_id" = r.id
                JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Questions_id" = tq."Questions_id"
                JOIN {S}."_nc_m2m_Answers_Court_Decisions" acd ON acd."Answers_id" = qa."Answers_id"
                WHERE acd."Court_Decisions_id" = v_id
            ), '[]'::jsonb),""",
    ),
    (
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Domestic_Instru" m ON m."Questions_id" = r.id
                WHERE m."Domestic_Instruments_id" = v_id
            ), '[]'::jsonb),""",
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                WHERE r.id IN (
                    SELECT qa."Questions_id"
                    FROM {S}."_nc_m2m_Answers_Domestic_Instru" adi
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = adi."Answers_id"
                    WHERE adi."Domestic_Instruments_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Domestic_Legal_" m ON m."Questions_id" = r.id
                WHERE m."Domestic_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),""",
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                WHERE r.id IN (
                    SELECT qa."Questions_id"
                    FROM {S}."_nc_m2m_Answers_Domestic_Legal_" adl
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = adl."Answers_id"
                    WHERE adl."Domestic_Legal_Provisions_id" = v_id
                    UNION
                    SELECT qa."Questions_id"
                    FROM {S}."_nc_m2m_Answers_Domestic_Legal_1" adl1
                    JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = adl1."Answers_id"
                    WHERE adl1."Domestic_Legal_Provisions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Regional_Legal_" m ON m."Questions_id" = r.id
                WHERE m."Regional_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),""",
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                WHERE r.id IN (
                    SELECT qa."Questions_id"
                    FROM {S}."_nc_m2m_HCCH_Answers_Regional_Legal_" hrl
                    JOIN {S}."_nc_m2m_Questions_HCCH_Answers" qa ON qa."HCCH_Answers_id" = hrl."HCCH_Answers_id"
                    WHERE hrl."Regional_Legal_Provisions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
    (
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_International_L" m ON m."Questions_id" = r.id
                WHERE m."International_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),""",
        """            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                WHERE r.id IN (
                    SELECT qa."Questions_id"
                    FROM {S}."_nc_m2m_HCCH_Answers_International_L" hil
                    JOIN {S}."_nc_m2m_Questions_HCCH_Answers" qa ON qa."HCCH_Answers_id" = hil."HCCH_Answers_id"
                    WHERE hil."International_Legal_Provisions_id" = v_id
                )
            ), '[]'::jsonb),""",
    ),
]


def _patched_detail_function(original: str, schema: str) -> str:
    text = original
    for raw_old, raw_new in PATCHES:
        old = raw_old.replace("{S}", schema)
        new = raw_new.replace("{S}", schema)
        occurrences = text.count(old)
        if occurrences != 1:
            label = old.splitlines()[3].strip() if len(old.splitlines()) >= 4 else old[:80]
            raise RuntimeError(f"Expected exactly 1 occurrence of patch target, found {occurrences}: {label!r}")
        text = text.replace(old, new, 1)
    return text


def upgrade() -> None:
    prior = _load_prior_module()
    op.execute(_patched_detail_function(prior.DETAIL_FUNCTION, prior.SCHEMA))


def downgrade() -> None:
    prior = _load_prior_module()
    op.execute(prior.DETAIL_FUNCTION)
