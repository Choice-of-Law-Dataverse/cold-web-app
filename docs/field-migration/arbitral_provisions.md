# Arbitral Provisions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Arbitral Rules ID` | `arbitralRulesId` | `arbitral_rules_id` | `Arbitral_Rules_CoLD_ID` | direct |
| `Article` | `article` | `article` | `Article` | direct |
| `Full Text (Original Language)` | `fullTextOriginalLanguage` | `full_text_original_language` | `Full_Text_of_the_Provision__Original_Language_` | direct |
| `Full Text (English Translation)` | `fullTextEnglishTranslation` | `full_text_english_translation` | `Full_Text_of_the_Provision__English_Translation_` | direct |
| `Arbitration method type` | `arbitrationMethodType` | `arbitration_method_type` | `Arbitration_method_type` | direct |
| `Non-State law allowed in AoC?` | `nonStateLawAllowedInAoc` | `non_state_law_allowed_in_aoc` | `Non_State_law_allowed_in_AoC_` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Arbitral Awards` | `arbitralAwards` | `arbitral_awards` | `related_arbitral_awards[*].Case_Number (joined by ', ')` | nested/array_join |
| `Arbitral Awards Link` | `arbitralAwardsLink` | `arbitral_awards_link` | `related_arbitral_awards[*].ncRecordId (joined by ',')` | nested/array_join |
| `Arbitral Institutions` | `arbitralInstitutions` | `arbitral_institutions` | `related_arbitral_institutions[*].Institution (joined by ', ')` | nested/array_join |
| `Arbitral Institutions Abbrev` | `arbitralInstitutionsAbbrev` | `arbitral_institutions_abbrev` | `related_arbitral_institutions[*].Abbreviation (joined by ', ')` | nested/array_join |
| `Arbitral Institutions Link` | `arbitralInstitutionsLink` | `arbitral_institutions_link` | `related_arbitral_institutions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Arbitral Rules` | `arbitralRules` | `arbitral_rules` | `related_arbitral_rules[*].Set_of_Rules (joined by ', ')` | nested/array_join |
| `Arbitral Rules In Force From` | `arbitralRulesInForceFrom` | `arbitral_rules_in_force_from` | `related_arbitral_rules[*].In_Force_From (joined by ', ')` | nested/array_join |
| `Arbitral Rules Link` | `arbitralRulesLink` | `arbitral_rules_link` | `related_arbitral_rules[*].ncRecordId (joined by ',')` | nested/array_join |
