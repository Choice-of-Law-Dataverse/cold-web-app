# Domestic Instruments -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `ID-number` | `idNumber` | `id_number` | `ID_Number` | direct |
| `Date` | `date` | `date` | `Date` | direct |
| `Status` | `status` | `status` | `Status` | direct |
| `Abbreviation` | `abbreviation` | `abbreviation` | `Abbreviation` | direct |
| `Relevant Provisions` | `relevantProvisions` | `relevant_provisions` | `Relevant_Provisions` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Entry Into Force` | `entryIntoForce` | `entry_into_force` | `Entry_Into_Force` | direct |
| `Publication Date` | `publicationDate` | `publication_date` | `Publication_Date` | direct |
| `Full Text of the Provisions` | `fullTextOfTheProvisions` | `full_text_of_the_provisions` | `Full_Text_of_the_Provisions` | direct |
| `Official Title` | `officialTitle` | `official_title` | `Official_Title` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(Date, updated_at)` | conditional |
| `Title (in English)` | `titleInEnglish` | `title_in_english` | `COALESCE(Title__in_English_, Official_Title)` | conditional |
| `Source (URL)` | `sourceUrl` | `source_url` | `COALESCE(Source__URL_, Official_Source_URL)` | conditional |
| `Source (PDF)` | `sourcePdf` | `source_pdf` | `COALESCE(Source__PDF_, Official_Source_PDF)` | conditional |
| `Compatible With the HCCH Principles` | `compatibleWithTheHcchPrinciples` | `compatible_with_the_hcch_principles` | `Compatible_With_the_HCCH_Principles_ (boolean: True/False)` | boolean |
| `Compatible With the UNCITRAL Model Law` | `compatibleWithTheUncitralModelLaw` | `compatible_with_the_uncitral_model_law` | `Compatible_With_the_UNCITRAL_Model_Law_ (boolean: True/False)` | boolean |
| `Source (PDF)` | `sourcePdf` | `source_pdf` | `Source__PDF_ (ComplexMappingType.JSON_EXTRACT.ComplexOperationType.FIRST_ITEM_AS_AIRTABLE_FORMAT)` | complex |
| `Jurisdictions Link` | `jurisdictionsLink` | `jurisdictions_link` | `related_jurisdictions[0].ncRecordId` | nested |
| `Jurisdictions Alpha-3 Code` | `jurisdictionsAlpha3Code` | `jurisdictions_alpha_3_code` | `related_jurisdictions[0].Alpha_3_Code` | nested |
| `Jurisdictions` | `jurisdictions` | `jurisdictions` | `related_jurisdictions[0].Name` | nested |
| `Type (from Jurisdictions)` | `typeFromJurisdictions` | `type_from_jurisdictions` | `related_jurisdictions[0].Type` | nested |
| `Question ID` | `questionId` | `question_id` | `related_questions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Answers Link` | `answersLink` | `answers_link` | `related_answers[*].ncRecordId (joined by ',')` | nested/array_join |
| `Domestic Legal Provisions Link` | `domesticLegalProvisionsLink` | `domestic_legal_provisions_link` | `related_legal_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Domestic Legal Provisions Full Text of the Provision (English T` | `domesticLegalProvisionsFullTextOfTheProvisionEnglishT` | `domestic_legal_provisions_full_text_of_the_provision_english_t` | `related_legal_provisions[*].Full_Text_of_the_Provision__English_Translation_ (joined by ',')` | nested/array_join |
| `Domestic Legal Provisions Full Text of the Provision (Original ` | `domesticLegalProvisionsFullTextOfTheProvisionOriginal` | `domestic_legal_provisions_full_text_of_the_provision_original` | `related_legal_provisions[*].Full_Text_of_the_Provision__Original_Language_ (joined by ',')` | nested/array_join |
| `Domestic Legal Provisions` | `domesticLegalProvisions` | `domestic_legal_provisions` | `related_legal_provisions[*].CoLD_ID (joined by ',')` | nested/array_join |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
