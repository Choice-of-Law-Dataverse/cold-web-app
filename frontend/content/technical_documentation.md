---
title: Technical Documentation — CoLD
description: Architecture, data model, public API, search behavior, technology stack, and deployment of the Choice of Law Dataverse.
---

## Platform Overview

The Choice of Law Dataverse (CoLD) is an open-access knowledge base about choice of law in international contracts. It brings together questionnaire answers, court decisions, legal instruments and provisions, arbitral materials, literature, jurisdictions, and specialists in a connected relational data model.

The platform is designed for researchers, legal practitioners, public authorities, international organizations, and educators. Visitors can browse linked records, compare jurisdictions, search across the Dataverse, download open data, and use the public API. Authenticated contributors can propose new records and corrections; submissions are reviewed before publication.

CoLD is developed at the University of Lucerne and licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Architecture

CoLD uses a multi-tier architecture in which editorial data management is separated from the public website and API.

| Layer           | Current implementation                                                                                                                    |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Data management | NocoDB provides the research team with an administrative interface for editing the relational source data.                                |
| Data storage    | PostgreSQL stores the structured records and relationships. Uploaded case-analysis documents are stored separately in Azure Blob Storage. |
| Query layer     | Versioned PostgreSQL views and functions flatten the NocoDB tables, build relationship data, and support full-text search.                |
| API             | A Python 3.12 FastAPI service validates requests and responses with Pydantic models and accesses PostgreSQL through SQLAlchemy.           |
| Website         | A Nuxt 4 application built with Vue and TypeScript renders the public interface and consumes the typed API.                               |

For public browsing, the data flow is:

1. Editors maintain records and links through NocoDB.
2. PostgreSQL views transform the source tables into stable search, list, and detail representations.
3. FastAPI exposes those representations as validated JSON responses.
4. The Nuxt website renders entity lists, detail pages, jurisdiction comparisons, statistics, and search results.

Browser requests from the website pass through a same-origin server proxy. This keeps application credentials on the server and forwards a signed-in user's Auth0 access token when an endpoint requires authentication. The public read-only API can also be called directly without an API key or user token.

## Technology Stack

| Area                             | Technologies                                                                     |
| -------------------------------- | -------------------------------------------------------------------------------- |
| Public website                   | Nuxt 4, Vue, TypeScript, Nuxt UI, Tailwind CSS, Nuxt Content, and TanStack Query |
| API                              | FastAPI, Python 3.12, Pydantic, and SQLAlchemy                                   |
| Database and editorial interface | PostgreSQL and NocoDB                                                            |
| Authentication                   | Auth0                                                                            |
| File storage                     | Azure Blob Storage                                                               |
| Hosting                          | Azure Container Apps and Azure Database for PostgreSQL                           |
| Observability                    | Logfire with OpenTelemetry instrumentation                                       |
| Delivery                         | Release Please, GitHub Actions, container images, and Cloudflare edge caching    |
| Preview deployments              | Vercel previews for pull-request branches                                        |

The source code and contribution instructions are available in the [CoLD web application repository](https://github.com/Choice-of-Law-Dataverse/cold-web-app).

## Data Model

The public API currently defines 17 datasets. The names below are the exact table names accepted by the bulk-export and record-detail endpoints.

| Dataset                        | Contents                                                                          |
| ------------------------------ | --------------------------------------------------------------------------------- |
| Answers                        | Jurisdiction-level responses to the standardized CoLD questionnaire               |
| HCCH Answers                   | Answers mapped to the HCCH Principles on Choice of Law                            |
| Questions                      | Standardized questionnaire items to which Answers respond                         |
| Court Decisions                | Case law with citations, dates, jurisdictions, themes, and choice-of-law analysis |
| Domestic Instruments           | National statutes, codes, and private international law regulations               |
| Domestic Legal Provisions      | Individual articles or provisions within domestic instruments                     |
| Regional Instruments           | Supranational instruments, including regional regulations and conventions         |
| Regional Legal Provisions      | Individual articles or provisions within regional instruments                     |
| International Instruments      | Treaties, conventions, principles, and model laws                                 |
| International Legal Provisions | Individual articles or provisions within international instruments                |
| Literature                     | Academic and practitioner publications about choice of law                        |
| Arbitral Awards                | Published arbitral awards with choice-of-law analysis                             |
| Arbitral Rules                 | Institutional arbitration rules                                                   |
| Arbitral Provisions            | Individual articles within arbitral rules                                         |
| Arbitral Institutions          | Institutions that administer arbitration proceedings                              |
| Jurisdictions                  | Countries and territories with regional and legal-family metadata                 |
| Specialists                    | Choice-of-law experts associated with jurisdictions and instruments               |

Themes connect questions to relevant decisions, instruments, provisions, answers, and literature. The glossary is maintained as explanatory website content rather than as a public API dataset.

Each published record has a CoLD ID. Prefixes identify the record type, and many IDs also include an ISO alpha-3 jurisdiction code. For example, `CD-CHE-1020` identifies a court decision from Switzerland. Original documents and attachments are stored separately from the structured metadata and linked to their records where publication rights permit.

For ready-made CSV and XLSX files, see [Data Sets](/learn/data-sets).

## Public API

The API follows OpenAPI 3.1. Its interactive reference and machine-readable schema are the authoritative sources for current paths, parameters, and response fields:

- [Interactive API reference](https://api.cold.global/api/v1/docs)
- [OpenAPI JSON schema](https://api.cold.global/api/v1/openapi.json)

Read-only data endpoints are public and require no API key or user token. Submitting suggestions or case analyses requires an Auth0 bearer token. Feedback can be submitted anonymously through the website, while signed-in users can associate feedback with their account. Moderation operations require an editor or administrator role.

### Core Read Endpoints

| Endpoint                                                      | Purpose                                                                             |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `GET /api/v1/search/`                                         | Full-text search with table, jurisdiction, and theme filters                        |
| `GET /api/v1/search/details`                                  | Fetch one record by exact table name and CoLD ID, including first-hop relationships |
| `GET /api/v1/search/full_table`                               | Return a complete dataset or filtered subset for bulk use                           |
| `GET /api/v1/search/specialists/{jurisdiction_alpha_code}`    | List specialists associated with a jurisdiction                                     |
| `GET /api/v1/entities/{slug}`                                 | Return a paginated, filterable entity catalogue                                     |
| `GET /api/v1/statistics/counts`                               | Return record counts per entity type                                                |
| `GET /api/v1/statistics/count-by-jurisdiction`                | Return per-jurisdiction counts for a selected table                                 |
| `GET /api/v1/statistics/jurisdictions-with-answer-percentage` | Return questionnaire coverage by jurisdiction                                       |

### Examples

Search for “party autonomy” and request 20 results:

```bash
curl "https://api.cold.global/api/v1/search/?search_string=party%20autonomy&page=1&page_size=20"
```

Fetch a court decision and its related records:

```bash
curl "https://api.cold.global/api/v1/search/details?table=Court%20Decisions&id=CD-CHE-42"
```

Export up to 100 court decisions, ordered by date:

```bash
curl "https://api.cold.global/api/v1/search/full_table?table=Court%20Decisions&limit=100&order_by=date&order_dir=desc"
```

The full-table endpoint also accepts repeatable `filter=column:value` parameters. The entity-list endpoint uses URL slugs such as `court-decisions`, accepts jurisdiction, theme, and entity-specific filters, and returns at most 250 records per page. Consult the OpenAPI reference before building an integration rather than relying on a copied list of fields.

## Search

CoLD search uses PostgreSQL full-text search with English-language normalization. Visitors can enter ordinary words without special operators. Common English word endings are normalized, so related forms can match, and common stop words do not dominate the ranking. CoLD IDs are included in the indexed text, which makes an exact identifier such as `CD-CHE-1020` a useful search query.

Searchable text is assembled from the identifiers and the most useful display and relationship fields for each supported record type. Depending on the dataset, this can include titles, citations, translations, provisions, questionnaire text and answers, abstracts, jurisdictions, legal families, themes, and linked records. These search documents are maintained in database views; the OpenAPI response models describe the fields returned to clients.

The search endpoint supports:

- repeatable `tables`, `jurisdictions`, and `themes` filters;
- `page` and `page_size` pagination, with at most 100 results per page; and
- `sort_by_date=true` for newest-first ordering where a meaningful date is available.

By default, matching records are ordered by relevance. Answers containing “No data” are moved behind substantive results. Court decisions with a case rank of 5 or below are also demoted, while remaining ordered from higher to lower case rank within that group. Stable table-name and record-ID tie-breakers keep pagination deterministic.

## Deployment and Operations

The public frontend and API are deployed as separate containers to Azure Container Apps, and PostgreSQL is hosted on Azure. Each application is versioned and released independently.

Production releases are automated with Release Please. A push to `main` updates a release pull request for each package with releasable changes. Merging a release pull request creates a `frontend-v*` or `backend-v*` tag, and that tag triggers the shared GitHub Actions deployment workflow for the corresponding package only. The workflow can also be dispatched manually as an operational fallback; a manual dispatch deploys both packages from the selected revision.

Backend releases build a versioned container image and update the `cold-backend` Azure Container App. Frontend releases load runtime configuration from Azure Key Vault, build a versioned image, update the `cold-frontend` Container App, and purge the Cloudflare cache when credentials are available. Vercel provides pull-request previews, but deployments from `main` and Release Please branches are disabled there; production is released through the tag-driven Azure workflow.

CoLD has one live production data environment. Local development runs the Nuxt and FastAPI services separately, but there is no development or staging copy of the production database. Database access and the NocoDB editorial interface are restricted to authorized team members; the public website and read-only API expose only publication-ready data.
