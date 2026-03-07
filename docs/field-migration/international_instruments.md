# International Instruments -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `ID Number` | `idNumber` | `id_number` | `ID_Number` | direct |
| `Title` | `title` | `title` | `Title` | direct |
| `Abbreviation` | `abbreviation` | `abbreviation` | `Abbreviation` | direct |
| `Date` | `date` | `date` | `Date` | direct |
| `Status` | `status` | `status` | `Status` | direct |
| `URL` | `url` | `url` | `URL` | direct |
| `Attachment` | `attachment` | `attachment` | `Attachment` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Entry Into Force` | `entryIntoForce` | `entry_into_force` | `Entry_Into_Force` | direct |
| `Publication Date` | `publicationDate` | `publication_date` | `Publication_Date` | direct |
| `Relevant Provisions` | `relevantProvisions` | `relevant_provisions` | `Relevant_Provisions` | direct |
| `Full Text of the Provisions` | `fullTextOfTheProvisions` | `full_text_of_the_provisions` | `Full_Text_of_the_Provisions` | direct |
| `Name` | `name` | `name` | `Name` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(updated_at, result_date)` | conditional |
| `Title (in English)` | `titleInEnglish` | `title_in_english` | `COALESCE(Title__in_English_, Official_Title)` | conditional |
| `Source (URL)` | `sourceUrl` | `source_url` | `COALESCE(Source__URL_, Official_Source_URL)` | conditional |
| `Source (PDF)` | `sourcePdf` | `source_pdf` | `COALESCE(Source__PDF_, Official_Source_PDF)` | conditional |
| `Literature` | `literature` | `literature` | `Literature_Link (array_extract.join_ids)` | complex |
| `Literature Link` | `literatureLink` | `literature_link` | `Literature_Link (array_extract.join_record_ids)` | complex |
| `International Legal Provisions` | `internationalLegalProvisions` | `international_legal_provisions` | `International_Legal_Provisions_Link (array_extract.join_display_values)` | complex |
| `International Legal Provisions Link` | `internationalLegalProvisionsLink` | `international_legal_provisions_link` | `International_Legal_Provisions_Link (array_extract.join_record_ids)` | complex |
| `Specialists` | `specialists` | `specialists` | `related_specialists[*].Specialist (joined by ',')` | nested/array_join |
| `Specialists Link` | `specialistsLink` | `specialists_link` | `related_specialists[*].ncRecordId (joined by ',')` | nested/array_join |
| `International Legal Provisions` | `internationalLegalProvisions` | `international_legal_provisions` | `related_legal_provisions[*].CoLD_ID (joined by ',')` | nested/array_join |
| `International Legal Provisions Link` | `internationalLegalProvisionsLink` | `international_legal_provisions_link` | `related_legal_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Literature` | `literature` | `literature` | `related_literature[*].CoLD_ID (joined by ',')` | nested/array_join |
| `Literature Link` | `literatureLink` | `literature_link` | `related_literature[*].ncRecordId (joined by ',')` | nested/array_join |
| `HCCH Answers` | `hcchAnswers` | `hcch_answers` | `related_hcch_answers[*].Adapted_Question (joined by ',')` | nested/array_join |
| `HCCH Answers Link` | `hcchAnswersLink` | `hcch_answers_link` | `related_hcch_answers[*].ncRecordId (joined by ',')` | nested/array_join |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
