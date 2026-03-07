# Arbitral Awards -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Case Number` | `caseNumber` | `case_number` | `Case_Number` | direct |
| `Context` | `context` | `context` | `Context` | direct |
| `Award Summary` | `awardSummary` | `award_summary` | `Award_Summary` | direct |
| `Year` | `year` | `year` | `Year` | direct |
| `Nature of the Award` | `natureOfTheAward` | `nature_of_the_award` | `Nature_of_the_Award` | direct |
| `Seat (Town)` | `seatTown` | `seat_town` | `Seat__Town_` | direct |
| `Source` | `source` | `source` | `Source` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(Year, updated_at)` | conditional |
| `Arbitral Institutions` | `arbitralInstitutions` | `arbitral_institutions` | `related_arbitral_institutions[*].Institution (joined by ', ')` | nested/array_join |
| `Arbitral Institutions Abbrev` | `arbitralInstitutionsAbbrev` | `arbitral_institutions_abbrev` | `related_arbitral_institutions[*].Abbreviation (joined by ', ')` | nested/array_join |
| `Arbitral Institutions Link` | `arbitralInstitutionsLink` | `arbitral_institutions_link` | `related_arbitral_institutions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Arbitral Provisions (Articles)` | `arbitralProvisionsArticles` | `arbitral_provisions_articles` | `related_arbitral_provisions[*].Article (joined by ', ')` | nested/array_join |
| `Arbitral Provisions Link` | `arbitralProvisionsLink` | `arbitral_provisions_link` | `related_arbitral_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Court Decisions` | `courtDecisions` | `court_decisions` | `related_court_decisions[*].Case_Title (joined by ', ')` | nested/array_join |
| `Court Decisions Link` | `courtDecisionsLink` | `court_decisions_link` | `related_court_decisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Jurisdictions` | `jurisdictions` | `jurisdictions` | `related_jurisdictions[*].Name (joined by ', ')` | nested/array_join |
| `Jurisdictions Alpha-3 Code` | `jurisdictionsAlpha3Code` | `jurisdictions_alpha_3_code` | `related_jurisdictions[*].Alpha_3_Code (joined by ',')` | nested/array_join |
| `Jurisdictions Link` | `jurisdictionsLink` | `jurisdictions_link` | `related_jurisdictions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Themes` | `themes` | `themes` | `related_themes[*].Theme (joined by ', ')` | nested/array_join |
