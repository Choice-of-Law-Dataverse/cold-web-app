# CoLD Database SQL Documentation

This directory contains the SQL setup and schema for the Choice of Law Dataverse (CoLD) database. The database uses PostgreSQL with a complex structure of base tables, junction tables for many-to-many relationships, and materialized views for optimized data retrieval.

## Database Architecture Overview

The database is organized into two main schemas:
- **`p1q5x3pj29vkrdr`** - Contains base tables and junction tables (NocoDB schema)
- **`data_views`** - Contains materialized views for optimized queries and search functionality

## Entity Relationship Diagram

This diagram shows the core entities and their relationships in the CoLD database:

```mermaid
erDiagram
    %% Core Legal Data Entities
    Jurisdictions {
        int id PK
        string Name
        string Alpha_3_Code
        string Legal_Families
    }
    
    Questions {
        int id PK
        string Question_Number
        string Primary_Theme
        text Question_Text
    }
    
    Themes {
        int id PK
        string Theme
    }
    
    Specialists {
        int id PK
        string Name
        string Email
        string Affiliation
    }
    
    %% Answer Systems
    Answers {
        int id PK
        text Answer
        text More_Information
        datetime updated_at
    }
    
    HCCH_Answers {
        int id PK
        text Answer
        text Citation
        datetime Date
    }
    
    %% Legal Instruments
    Domestic_Instruments {
        int id PK
        string Title
        string Abbreviation
        string ID_Number
        date Date
    }
    
    Regional_Instruments {
        int id PK
        string Title
        string Abbreviation
        string ID_Number
        date Date
    }
    
    International_Instruments {
        int id PK
        string Name
        string Title
        string ID_Number
        date Date
    }
    
    %% Legal Provisions
    Domestic_Legal_Provisions {
        int id PK
        string Provision
        text Text
    }
    
    Regional_Legal_Provisions {
        int id PK
        string Provision
        text Text
    }
    
    International_Legal_Provisions {
        int id PK
        string Provision
        text Text
    }
    
    %% Court System
    Court_Decisions {
        int id PK
        string Case_Name
        string Citation
        date Date
        int Case_Rank
    }
    
    %% Literature
    Literature {
        int id PK
        string Title
        string Author
        string ID_Number
        date Date
    }
    
    %% Arbitration
    Arbitral_Awards {
        int id PK
        string Case_Name
        string Citation
        date Date
    }
    
    Arbitral_Institutions {
        int id PK
        string Name
        string Abbreviation
        string ID_Number
    }
    
    Arbitral_Rules {
        int id PK
        string Title
        string ID_Number
        date Date
    }
    
    Arbitral_Provisions {
        int id PK
        string Provision
        text Text
    }
    
    %% Core Relationships
    Questions ||--o{ Themes : "categorized by"
    Questions ||--o{ Answers : "answered by"
    Jurisdictions ||--o{ Answers : "provides"
    
    %% Instrument Relationships
    Domestic_Instruments ||--o{ Domestic_Legal_Provisions : "contains"
    Regional_Instruments ||--o{ Regional_Legal_Provisions : "contains"
    International_Instruments ||--o{ International_Legal_Provisions : "contains"
    
    %% Jurisdiction Connections
    Jurisdictions ||--o{ Court_Decisions : "issues"
    Jurisdictions ||--o{ Literature : "produces"
    Jurisdictions ||--o{ Domestic_Instruments : "enacts"
    Jurisdictions ||--o{ Specialists : "has"
    
    %% Cross-References
    Answers ||--o{ Court_Decisions : "references"
    Answers ||--o{ Literature : "cites"
    Answers ||--o{ Domestic_Instruments : "mentions"
    
    %% Arbitration Relationships
    Arbitral_Institutions ||--o{ Arbitral_Awards : "issues"
    Arbitral_Institutions ||--o{ Arbitral_Rules : "adopts"
    Arbitral_Rules ||--o{ Arbitral_Provisions : "contains"
    Arbitral_Awards ||--o{ Arbitral_Provisions : "applies"
    
    %% Theme Associations
    Themes ||--o{ Literature : "categorizes"
    Themes ||--o{ HCCH_Answers : "categorizes"
    Themes ||--o{ Arbitral_Awards : "categorizes"
    
    %% Specialist Connections
    Specialists ||--o{ Regional_Instruments : "advises on"
    Specialists ||--o{ International_Instruments : "contributes to"
    
    %% International System
    International_Instruments ||--o{ HCCH_Answers : "informs"
    International_Instruments ||--o{ Literature : "referenced in"
```

## Materialized Views Architecture

The database uses materialized views to provide optimized, pre-computed data sets. There are two types of materialized views:

### Complete Views (`*_complete`)
These views include full records with all related data as JSON aggregates:

```mermaid
graph TD
    %% Base Tables
    BT[Base Tables<br/>p1q5x3pj29vkrdr.*] --> CV[Complete Views<br/>data_views.*_complete]
    JT[Junction Tables<br/>_nc_m2m_*] --> CV
    
    %% Complete Views
    CV --> QC[questions_complete]
    CV --> AC[answers_complete]
    CV --> HAC[hcch_answers_complete]
    CV --> DIC[domestic_instruments_complete]
    CV --> DLPC[domestic_legal_provisions_complete]
    CV --> RIC[regional_instruments_complete]
    CV --> RLPC[regional_legal_provisions_complete]
    CV --> IIC[international_instruments_complete]
    CV --> ILPC[international_legal_provisions_complete]
    CV --> CDC[court_decisions_complete]
    CV --> LC[literature_complete]
    CV --> AAC[arbitral_awards_complete]
    CV --> AINC[arbitral_institutions_complete]
    CV --> ARC[arbitral_rules_complete]
    CV --> APC[arbitral_provisions_complete]
    CV --> JC[jurisdictions_complete]
    
    %% Search Views
    CV --> SV[Search Views<br/>data_views.* (without _complete)]
    SV --> AS[answers]
    SV --> HAS[hcch_answers]
    SV --> CDS[court_decisions]
    SV --> DIS[domestic_instruments]
    SV --> RIS[regional_instruments]
    SV --> IIS[international_instruments]
    SV --> LS[literature]
    
    %% Search Function
    SV --> SF[search_all function]
    SF --> API[FastAPI Search Endpoints]
```

### Search Views (without `_complete`)
These views are optimized for full-text search with tsvector columns:

```mermaid
graph LR
    %% Search Architecture
    subgraph "Full-Text Search System"
        FTS[Full-Text Search Views] --> TSV[tsvector columns]
        TSV --> GIN[GIN Indexes]
        GIN --> SF[search_all function]
    end
    
    subgraph "Search Views"
        SV1[data_views.answers]
        SV2[data_views.court_decisions]
        SV3[data_views.literature]
        SV4[data_views.domestic_instruments]
        SV5[data_views.regional_instruments]
        SV6[data_views.international_instruments]
        SV7[data_views.hcch_answers]
    end
    
    SV1 --> FTS
    SV2 --> FTS
    SV3 --> FTS
    SV4 --> FTS
    SV5 --> FTS
    SV6 --> FTS
    SV7 --> FTS
    
    SF --> PAGINATED[Paginated Results]
    SF --> FILTERED[Filtered by Jurisdiction/Theme]
    SF --> RANKED[Relevance Ranked]
```

## Data Flow and Transformation Pipeline

```mermaid
graph TD
    %% Data Sources
    NOCODB[NocoDB Interface] --> BASE[Base Tables<br/>p1q5x3pj29vkrdr.*]
    API[API Uploads] --> BASE
    
    %% Core Processing
    BASE --> REFRESH[refresh_all_materialized_views]
    
    %% View Generation
    REFRESH --> COMPLETE[Complete Views<br/>WITH JSON Aggregates]
    REFRESH --> SEARCH[Search Views<br/>WITH tsvector]
    
    %% Application Layer
    COMPLETE --> FASTAPI[FastAPI Backend]
    SEARCH --> FASTAPI
    
    %% API Endpoints
    FASTAPI --> FULL[Full Table Queries]
    FASTAPI --> SEARCHAPI[Search Endpoints]
    FASTAPI --> DETAILS[Detail Views]
    
    %% Frontend
    FULL --> FRONTEND[Frontend Application]
    SEARCHAPI --> FRONTEND
    DETAILS --> FRONTEND
    
    %% Utility Functions
    FASTAPI --> TRANSFORM[Data Transformers<br/>app/mapping/]
    TRANSFORM --> FRONTEND
```

## Key Features

### 1. **Comprehensive Data Model**
- **18 base tables** covering all aspects of choice of law data
- **32 junction tables** for many-to-many relationships
- **23 materialized views** for optimized queries

### 2. **Advanced Search Capabilities**
- Full-text search across all entity types
- Jurisdiction and theme filtering
- Relevance ranking with custom business rules
- Pagination and sorting

### 3. **Data Integrity**
- Unique indexes on all materialized views
- Concurrent refresh capability for high-availability
- Automatic refresh function for all views

### 4. **Performance Optimization**
- Pre-computed JSON aggregates in complete views
- GIN indexes on tsvector columns for fast text search
- Materialized views reduce complex join overhead

## Refresh Strategy

The materialized views are refreshed using the `data_views.refresh_all_materialized_views()` function:

```sql
-- Manual refresh of all views
SELECT data_views.refresh_all_materialized_views();
```

This function:
- Detects views with unique indexes for concurrent refresh
- Falls back to non-concurrent refresh when needed
- Provides logging for monitoring refresh operations

## Files in this Directory

- **`setup.sql`** - Main database schema and materialized view definitions
- **`nocodb_schema.sql`** - Query for exploring NocoDB table structure
- **`fts-with-filters.sql`** - Full-text search with filtering examples
- **`hop-1-graph.sql`** - Graph queries for relationship analysis
- **`cron_job.sql`** - Scheduled maintenance operations

## Development Guidelines

1. **Adding New Views**: Follow the naming convention `data_views.{entity}_complete` for complete views and `data_views.{entity}` for search views
2. **Indexing**: Always add unique indexes to materialized views to enable concurrent refresh
3. **Search Integration**: Include tsvector columns in search views for full-text search capability
4. **Testing**: Use the backend test suite to validate view functionality after changes

For more details on the data transformation system, see the backend documentation in `backend/app/mapping/`.