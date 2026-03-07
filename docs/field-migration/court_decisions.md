# Court Decisions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Case Citation` | `caseCitation` | `case_citation` | `Case_Citation` | direct |
| `Case Title` | `caseTitle` | `case_title` | `Case_Title` | direct |
| `Instance` | `instance` | `instance` | `Instance` | direct |
| `Date` | `date` | `date` | `Date` | direct |
| `Abstract` | `abstract` | `abstract` | `Abstract` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `ID-number` | `idNumber` | `id_number` | `ID_number` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Added By.id` | `addedById` | `added_by_id` | `created_by` | direct |
| `Created time` | `createdTime` | `created_time` | `Created` | direct |
| `Answers Link` | `answersLink` | `answers_link` | `Answers_Link` | direct |
| `Answers Question` | `answersQuestion` | `answers_question` | `Answers_Question` | direct |
| `Text_of_the_Relevant_Legal_Provisions` | `textOfTheRelevantLegalProvisions` | `text_of_the_relevant_legal_provisions` | `Text_of_the_Relevant_Legal_Provisions` | direct |
| `Quote` | `quote` | `quote` | `Quote` | direct |
| `Case Rank` | `caseRank` | `case_rank` | `Case_Rank` | direct |
| `English Translation` | `englishTranslation` | `english_translation` | `English_Translation` | direct |
| `Choice of Law Issue` | `choiceOfLawIssue` | `choice_of_law_issue` | `Choice_of_Law_Issue` | direct |
| `Court's Position` | `courtSPosition` | `court_s_position` | `Court's_Position` | direct |
| `Translated Excerpt` | `translatedExcerpt` | `translated_excerpt` | `Translated_Excerpt` | direct |
| `Relevant Facts` | `relevantFacts` | `relevant_facts` | `Relevant_Facts` | direct |
| `Date of Judgment` | `dateOfJudgment` | `date_of_judgment` | `Date_of_Judgment` | direct |
| `PIL Provisions` | `pilProvisions` | `pil_provisions` | `PIL_Provisions` | direct |
| `Original Text` | `originalText` | `original_text` | `Original_Text` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(Publication_Date_ISO, updated_at)` | conditional |
| `Publication Date ISO` | `publicationDateIso` | `publication_date_iso` | `COALESCE(Publication_Date_ISO, Date)` | conditional |
| `Official Source (URL)` | `officialSourceUrl` | `official_source_url` | `COALESCE(Official_Source__URL_, Official_Source_URL)` | conditional |
| `Official Source (PDF)` | `officialSourcePdf` | `official_source_pdf` | `Official_Source__PDF_ (ComplexMappingType.JSON_EXTRACT.ComplexOperationType.FIRST_ITEM_AS_AIRTABLE_FORMAT)` | complex |
| `Questions` | `questions` | `questions` | `related_questions[*].CoLD_ID (joined by ',')` | nested/array_join |
| `Jurisdictions Link` | `jurisdictionsLink` | `jurisdictions_link` | `related_jurisdictions[0].ncRecordId` | nested |
| `Jurisdictions Alpha-3 Code` | `jurisdictionsAlpha3Code` | `jurisdictions_alpha_3_code` | `related_jurisdictions[0].Alpha_3_Code` | nested |
| `Jurisdictions` | `jurisdictions` | `jurisdictions` | `related_jurisdictions[0].Name` | nested |
| `Region (from Jurisdictions)` | `regionFromJurisdictions` | `region_from_jurisdictions` | `related_jurisdictions[0].Region` | nested |
| `Themes` | `themes` | `themes` | `related_themes[*].Theme (joined by ',')` | nested/array_join |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Added By.id` | `addedById` | `added_by_id` | `created_by.id` | user |
| `Added By.email` | `addedByEmail` | `added_by_email` | `created_by.email` | user |
| `Added By.name` | `addedByName` | `added_by_name` | `created_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
