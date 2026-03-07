# Answers -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Answer` | `answer` | `answer` | `Answer` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `To Review?` | `toReview` | `to_review` | `To_Review_` | direct |
| `OUP Book Quote` | `oupBookQuote` | `oup_book_quote` | `OUP_Book_Quote` | direct |
| `More Information` | `moreInformation` | `more_information` | `More_Information` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(updated_at, result_date)` | conditional |
| `Question Link` | `questionLink` | `question_link` | `related_questions[0].ncRecordId` | nested |
| `Question` | `question` | `question` | `related_questions[0].Question` | nested |
| `Number` | `number` | `number` | `related_questions[0].Question_Number` | nested |
| `Questions Theme Code` | `questionsThemeCode` | `questions_theme_code` | `related_questions[0].COALESCE(Theme_Code, Primary_Theme)` | nested/conditional |
| `Jurisdictions Link` | `jurisdictionsLink` | `jurisdictions_link` | `related_jurisdictions[0].ncRecordId` | nested |
| `Jurisdictions Alpha-3 Code` | `jurisdictionsAlpha3Code` | `jurisdictions_alpha_3_code` | `related_jurisdictions[0].Alpha_3_Code` | nested |
| `Jurisdictions Alpha-3 code` | `jurisdictionsAlpha3Code` | `jurisdictions_alpha_3_code` | `related_jurisdictions[0].Alpha_3_Code` | nested |
| `Jurisdictions` | `jurisdictions` | `jurisdictions` | `related_jurisdictions[0].Name` | nested |
| `Jurisdictions Region` | `jurisdictionsRegion` | `jurisdictions_region` | `related_jurisdictions[0].Region` | nested |
| `Jurisdictions Irrelevant` | `jurisdictionsIrrelevant` | `jurisdictions_irrelevant` | `related_jurisdictions[0].Irrelevant_ (boolean)` | nested/boolean |
| `Court Decisions` | `courtDecisions` | `court_decisions` | `hop1_relations.related_court_decisions[*].Case_Title (joined by ',')` | nested/array_join |
| `Court Decisions Link` | `courtDecisionsLink` | `court_decisions_link` | `hop1_relations.related_court_decisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Court Decisions ID` | `courtDecisionsId` | `court_decisions_id` | `hop1_relations.related_court_decisions[*].CoLD_ID (joined by ',')` | nested/array_join |
| `Domestic Instruments Link` | `domesticInstrumentsLink` | `domestic_instruments_link` | `hop1_relations.related_domestic_instruments[0].ncRecordId` | nested |
| `Domestic Instruments` | `domesticInstruments` | `domestic_instruments` | `hop1_relations.related_domestic_instruments[0].Official_Title` | nested |
| `Domestic Instruments ID` | `domesticInstrumentsId` | `domestic_instruments_id` | `hop1_relations.related_domestic_instruments[0].CoLD_ID` | nested |
| `Domestic Legal Provisions Link` | `domesticLegalProvisionsLink` | `domestic_legal_provisions_link` | `hop1_relations.related_domestic_legal_provisions[0].ncRecordId` | nested |
| `Domestic Legal Provisions` | `domesticLegalProvisions` | `domestic_legal_provisions` | `hop1_relations.related_domestic_legal_provisions[0].CoLD_ID` | nested |
| `Themes` | `themes` | `themes` | `related_themes[*].Theme (joined by ', ')` | nested/array_join |
