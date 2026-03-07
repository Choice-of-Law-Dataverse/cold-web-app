# Domestic Legal Provisions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Name` | `name` | `name` | `CoLD_ID` | direct |
| `Article` | `article` | `article` | `Article` | direct |
| `Full Text of the Provision (Original Language)` | `fullTextOfTheProvisionOriginalLanguage` | `full_text_of_the_provision_original_language` | `Full_Text_of_the_Provision__Original_Language_` | direct |
| `Full Text of the Provision (English Translation)` | `fullTextOfTheProvisionEnglishTranslation` | `full_text_of_the_provision_english_translation` | `Full_Text_of_the_Provision__English_Translation_` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Ranking (Display Order)` | `rankingDisplayOrder` | `ranking_display_order` | `Ranking__Display_Order_` | direct |
| `Domestic Instruments Link` | `domesticInstrumentsLink` | `domestic_instruments_link` | `related_domestic_instruments[0].ncRecordId` | nested |
| `Legislation Title` | `legislationTitle` | `legislation_title` | `related_domestic_instruments[0].Title__in_English_` | nested |
| `Answers` | `answers` | `answers` | `related_answers[*].ncRecordId (joined by ',')` | nested/array_join |
| `Questions` | `questions` | `questions` | `related_questions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Themes Link` | `themesLink` | `themes_link` | `related_themes[*].ncRecordId (joined by ',')` | nested/array_join |
| `Jurisdictions Link` | `jurisdictionsLink` | `jurisdictions_link` | `related_jurisdictions[0].ncRecordId` | nested |
| `Jurisdictions` | `jurisdictions` | `jurisdictions` | `related_jurisdictions[0].Name` | nested |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
