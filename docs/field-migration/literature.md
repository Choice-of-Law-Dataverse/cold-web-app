# Literature -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `CoLD_ID` | `coldId` | `cold_id` | `CoLD_ID` | direct |
| `Key` | `key` | `key` | `Key` | direct |
| `Item Type` | `itemType` | `item_type` | `Item_Type` | direct |
| `Publication Year` | `publicationYear` | `publication_year` | `Publication_Year` | direct |
| `Author` | `author` | `author` | `Author` | direct |
| `Title` | `title` | `title` | `Title` | direct |
| `ISBN` | `isbn` | `isbn` | `ISBN` | direct |
| `ISSN` | `issn` | `issn` | `ISSN` | direct |
| `Url` | `url` | `url` | `Url` | direct |
| `Date` | `date` | `date` | `Date` | direct |
| `Date Added` | `dateAdded` | `date_added` | `Date_Added` | direct |
| `Date Modified` | `dateModified` | `date_modified` | `Date_Modified` | direct |
| `Publisher` | `publisher` | `publisher` | `Publisher` | direct |
| `Language` | `language` | `language` | `Language` | direct |
| `Extra` | `extra` | `extra` | `Extra` | direct |
| `Manual Tags` | `manualTags` | `manual_tags` | `Manual_Tags` | direct |
| `Editor` | `editor` | `editor` | `Editor` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Publication Title` | `publicationTitle` | `publication_title` | `Publication_Title` | direct |
| `Issue` | `issue` | `issue` | `Issue` | direct |
| `Volume` | `volume` | `volume` | `Volume` | direct |
| `Pages` | `pages` | `pages` | `Pages` | direct |
| `Abstract Note` | `abstractNote` | `abstract_note` | `Abstract_Note` | direct |
| `Library Catalog` | `libraryCatalog` | `library_catalog` | `Library_Catalog` | direct |
| `DOI` | `doi` | `doi` | `DOI` | direct |
| `Access Date` | `accessDate` | `access_date` | `Access_Date` | direct |
| `Open Access` | `openAccess` | `open_access` | `Open_Access` | direct |
| `Open Access URL` | `openAccessUrl` | `open_access_url` | `Open_Access_URL` | direct |
| `Journal Abbreviation` | `journalAbbreviation` | `journal_abbreviation` | `Journal_Abbreviation` | direct |
| `Short Title` | `shortTitle` | `short_title` | `Short_Title` | direct |
| `Place` | `place` | `place` | `Place` | direct |
| `Num Pages` | `numPages` | `num_pages` | `Num_Pages` | direct |
| `Type` | `type` | `type` | `Type` | direct |
| `OUP JD Chapter` | `oupJdChapter` | `oup_jd_chapter` | `OUP_JD_Chapter` | direct |
| `Contributor` | `contributor` | `contributor` | `Contributor` | direct |
| `Automatic Tags` | `automaticTags` | `automatic_tags` | `Automatic_Tags` | direct |
| `Number` | `number` | `number` | `Number` | direct |
| `Series` | `series` | `series` | `Series` | direct |
| `Series Number` | `seriesNumber` | `series_number` | `Series_Number` | direct |
| `Series Editor` | `seriesEditor` | `series_editor` | `Series_Editor` | direct |
| `Edition` | `edition` | `edition` | `Edition` | direct |
| `Call Number` | `callNumber` | `call_number` | `Call_Number` | direct |
| `Jurisdiction Summary` | `jurisdictionSummary` | `jurisdiction_summary` | `Jurisdiction_Summary` | direct |
| `Answers` | `answers` | `answers` | `Answers` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(Date, Publication_Year)` | conditional |
| `International Instruments` | `internationalInstruments` | `international_instruments` | `International_Instruments_Link (array_extract.join_display_values)` | complex |
| `International Instruments Link` | `internationalInstrumentsLink` | `international_instruments_link` | `International_Instruments_Link (array_extract.join_record_ids)` | complex |
| `International Legal Provisions` | `internationalLegalProvisions` | `international_legal_provisions` | `International_Legal_Provisions_Link (array_extract.join_display_values)` | complex |
| `International Legal Provisions Link` | `internationalLegalProvisionsLink` | `international_legal_provisions_link` | `International_Legal_Provisions_Link (array_extract.join_record_ids)` | complex |
| `Regional Instruments` | `regionalInstruments` | `regional_instruments` | `Regional_Instruments_Link (array_extract.join_display_values)` | complex |
| `Regional Instruments Link` | `regionalInstrumentsLink` | `regional_instruments_link` | `Regional_Instruments_Link (array_extract.join_record_ids)` | complex |
| `Jurisdiction Link` | `jurisdictionLink` | `jurisdiction_link` | `related_jurisdictions[0].ncRecordId` | nested |
| `Jurisdiction` | `jurisdiction` | `jurisdiction` | `related_jurisdictions[0].Name` | nested |
| `Themes` | `themes` | `themes` | `related_themes[*].Theme (joined by ',')` | nested/array_join |
| `Themes Link` | `themesLink` | `themes_link` | `related_themes[*].ncRecordId (joined by ',')` | nested/array_join |
| `International Instruments` | `internationalInstruments` | `international_instruments` | `related_international_instruments[*].Name (joined by ',')` | nested/array_join |
| `International Instruments Link` | `internationalInstrumentsLink` | `international_instruments_link` | `related_international_instruments[*].ncRecordId (joined by ',')` | nested/array_join |
| `International Instruments` | `internationalInstruments` | `international_instruments` | `hop1_relations.related_international_instruments[*].Name (joined by ',')` | nested/array_join |
| `International Instruments Link` | `internationalInstrumentsLink` | `international_instruments_link` | `hop1_relations.related_international_instruments[*].ncRecordId (joined by ',')` | nested/array_join |
| `International Legal Provisions` | `internationalLegalProvisions` | `international_legal_provisions` | `related_international_legal_provisions[*].Title_of_the_Provision (joined by ',')` | nested/array_join |
| `International Legal Provisions Link` | `internationalLegalProvisionsLink` | `international_legal_provisions_link` | `related_international_legal_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `International Legal Provisions` | `internationalLegalProvisions` | `international_legal_provisions` | `hop1_relations.related_international_legal_provisions[*].Title_of_the_Provision (joined by ',')` | nested/array_join |
| `International Legal Provisions Link` | `internationalLegalProvisionsLink` | `international_legal_provisions_link` | `hop1_relations.related_international_legal_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Regional Instruments` | `regionalInstruments` | `regional_instruments` | `hop1_relations.related_regional_instruments[*].Name (joined by ',')` | nested/array_join |
| `Regional Instruments Link` | `regionalInstrumentsLink` | `regional_instruments_link` | `hop1_relations.related_regional_instruments[*].ncRecordId (joined by ',')` | nested/array_join |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
