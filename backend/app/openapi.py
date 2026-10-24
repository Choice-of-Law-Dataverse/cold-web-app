"""OpenAPI metadata shown in the generated API documentation."""

from typing import Any

TITLE = "CoLD API — Choice of Law Dataverse"

DESCRIPTION = (
    "# Choice of Law Dataverse (CoLD) API\n\n"
    "Open-access REST API for the **[Choice of Law Dataverse](https://cold.global)**, "
    "a curated knowledge base on choice of law in international contracts. "
    "CoLD is an SNF-funded project at the University of Lucerne, licensed under "
    "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
    "Winner of the Swiss National ORD Prize 2025.\n\n"
    "## Available datasets\n\n"
    "| Table name | Description |\n"
    "|---|---|\n"
    "| **Answers** | Country-level responses to the CoLD standardised questionnaire on choice-of-law rules |\n"
    "| **HCCH Answers** | Answers mapped to the HCCH Principles on Choice of Law |\n"
    "| **Questions** | The standardised questionnaire items that Answers respond to |\n"
    "| **Court Decisions** | Case law with metadata, themes, PIL provisions, and jurisdiction links |\n"
    "| **Domestic Instruments** | National statutes, codes, and PIL regulations |\n"
    "| **Domestic Legal Provisions** | Individual articles/provisions within domestic instruments |\n"
    "| **Regional Instruments** | Supranational instruments (e.g. EU Rome I Regulation) |\n"
    "| **Regional Legal Provisions** | Individual articles/provisions within regional instruments |\n"
    "| **International Instruments** | Treaties, conventions, and model laws (e.g. HCCH Principles) |\n"
    "| **International Legal Provisions** | Individual articles/provisions within international instruments |\n"
    "| **Literature** | Academic and practitioner publications on choice of law |\n"
    "| **Arbitral Awards** | Published arbitral awards with choice-of-law analysis |\n"
    "| **Arbitral Rules** | Institutional arbitration rules (e.g. ICC, LCIA) |\n"
    "| **Arbitral Provisions** | Individual articles within arbitral rules |\n"
    "| **Arbitral Institutions** | Arbitration institutions (e.g. ICC, SIAC) |\n"
    "| **Jurisdictions** | Countries and territories with metadata (region, legal family) |\n"
    "| **Specialists** | Choice-of-law experts by jurisdiction |\n\n"
    "Bulk CSV/XLSX exports are also available at "
    "[cold.global/learn/data-sets](https://cold.global/learn/data-sets). "
    "Architecture, data model, and search documentation are available at "
    "[cold.global/learn/technical-documentation]"
    "(https://cold.global/learn/technical-documentation).\n\n"
    "## Quick start for data scientists\n\n"
    "1. **Search** — `GET /api/v1/search/?search_string=party+autonomy` "
    "returns paginated results across all datasets.\n"
    "2. **Bulk export** — `GET /api/v1/search/full_table?table=Court+Decisions` "
    "returns every record in a table (see table names above).\n"
    "3. **Record detail** — `GET /api/v1/search/details?table=Court+Decisions&id=CD-CHE-42` "
    "returns a single record with its related entities.\n"
    "4. **Entity lists** — `GET /api/v1/entities/court-decisions?jurisdiction=CHE` "
    "returns paginated, filterable entity catalogues.\n"
    "5. **Statistics** — `GET /api/v1/statistics/counts` "
    "returns record counts per entity type, optionally scoped to a jurisdiction.\n\n"
    "## Glossary\n\n"
    "Key private international law terms used throughout the API "
    "(party autonomy, dépeçage, PIL codification, mandatory rules, etc.) "
    "are defined in the [CoLD Glossary](https://cold.global/learn/glossary).\n\n"
    "## Authentication\n\n"
    "**Read-only data endpoints are publicly accessible — no API key or token required.**\n\n"
    "Submitting suggestions or case analyses requires an Auth0 JWT "
    "in the `Authorization: Bearer <token>` header. Feedback may be submitted anonymously. "
    "Moderation endpoints additionally require editor or admin roles.\n"
)

CONTACT = {
    "name": "CoLD Team — University of Lucerne",
    "url": "https://cold.global",
}

LICENSE_INFO = {
    "name": "CC BY 4.0",
    "url": "https://creativecommons.org/licenses/by/4.0/",
}

TAGS: list[dict[str, Any]] = [
    {
        "name": "Search",
        "description": (
            "Core data-access endpoints. Full-text search across all datasets with faceted filtering "
            "(by table, jurisdiction, theme), entity detail retrieval by CoLD ID, bulk table export, "
            "and specialist lookup by jurisdiction."
        ),
    },
    {
        "name": "Entities",
        "description": (
            "Paginated entity lists per type (court decisions, instruments, literature, etc.) with "
            "optional jurisdiction and theme filters. Useful for building filtered views or exporting "
            "entity catalogues."
        ),
    },
    {
        "name": "Statistics",
        "description": (
            "Aggregate metrics: record counts per entity type, jurisdiction-level answer coverage "
            "percentages, and per-table jurisdiction breakdowns."
        ),
    },
    {
        "name": "AI",
        "description": (
            "AI-powered helpers. Currently exposes a query classifier that maps free-text questions "
            "to predefined CoLD thematic categories."
        ),
    },
    {
        "name": "Case Analyzer",
        "description": (
            "Multi-step court decision analysis workflow. Upload a PDF, extract text, detect jurisdiction, "
            "and run AI-powered extraction (themes, citations, PIL provisions, etc.). "
            "Results stream as Server-Sent Events. Requires authentication."
        ),
    },
    {
        "name": "LandingPage",
        "description": "Helper endpoints for the CoLD landing page, including jurisdiction data-availability flags.",
    },
    {
        "name": "Suggestions",
        "description": (
            "Community data contributions. Authenticated users can submit new court decisions, instruments, "
            "or literature entries for moderator review. Editors/admins manage the moderation queue."
        ),
    },
    {
        "name": "Feedback",
        "description": (
            "Entity-level feedback. Users can report errors or suggest corrections on existing records. "
            "Editors/admins triage and resolve feedback items."
        ),
    },
    {
        "name": "Submarine",
        "description": "Easter egg.",
    },
]
