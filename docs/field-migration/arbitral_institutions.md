# Arbitral Institutions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Institution` | `institution` | `institution` | `Institution` | direct |
| `Abbreviation` | `abbreviation` | `abbreviation` | `Abbreviation` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Arbitral Awards` | `arbitralAwards` | `arbitral_awards` | `related_arbitral_awards[*].Case_Number (joined by ', ')` | nested/array_join |
| `Arbitral Awards Link` | `arbitralAwardsLink` | `arbitral_awards_link` | `related_arbitral_awards[*].ncRecordId (joined by ',')` | nested/array_join |
| `Arbitral Rules` | `arbitralRules` | `arbitral_rules` | `related_arbitral_rules[*].Set_of_Rules (joined by ', ')` | nested/array_join |
| `Arbitral Rules In Force From` | `arbitralRulesInForceFrom` | `arbitral_rules_in_force_from` | `related_arbitral_rules[*].In_Force_From (joined by ', ')` | nested/array_join |
| `Arbitral Rules Link` | `arbitralRulesLink` | `arbitral_rules_link` | `related_arbitral_rules[*].ncRecordId (joined by ',')` | nested/array_join |
| `Arbitral Provisions (Articles)` | `arbitralProvisionsArticles` | `arbitral_provisions_articles` | `related_arbitral_provisions[*].Article (joined by ', ')` | nested/array_join |
| `Arbitral Provisions Link` | `arbitralProvisionsLink` | `arbitral_provisions_link` | `related_arbitral_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Jurisdictions` | `jurisdictions` | `jurisdictions` | `related_jurisdictions[*].Name (joined by ', ')` | nested/array_join |
| `Jurisdictions Alpha-3 Code` | `jurisdictionsAlpha3Code` | `jurisdictions_alpha_3_code` | `related_jurisdictions[*].Alpha_3_Code (joined by ',')` | nested/array_join |
| `Jurisdictions Link` | `jurisdictionsLink` | `jurisdictions_link` | `related_jurisdictions[*].ncRecordId (joined by ',')` | nested/array_join |
