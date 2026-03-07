# International Legal Provisions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `cold_id` | `coldId` | `cold_id` | `CoLD_ID` | direct |
| `CoLD_ID` | `coldId` | `cold_id` | `CoLD_ID` | direct |
| `Title of the Provision` | `titleOfTheProvision` | `title_of_the_provision` | `Title_of_the_Provision` | direct |
| `Full Text` | `fullText` | `full_text` | `Full_Text` | direct |
| `Provision` | `provision` | `provision` | `Provision` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Ranking__Display_Order_` | `rankingDisplayOrder` | `ranking_display_order` | `Ranking__Display_Order_` | direct |
| `nc_order` | `ncOrder` | `nc_order` | `nc_order` | direct |
| `ncRecordHash` | `ncrecordhash` | `ncrecordhash` | `ncRecordHash` | direct |
| `Arbitral_Awards` | `arbitralAwards` | `arbitral_awards` | `Arbitral_Awards` | direct |
| `Instrument_CoLD_ID` | `instrumentColdId` | `instrument_cold_id` | `Instrument_CoLD_ID` | direct |
| `International_Instruments_copy` | `internationalInstrumentsCopy` | `international_instruments_copy` | `International_Instruments_copy` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(updated_at, result_date)` | conditional |
| `Instrument` | `instrument` | `instrument` | `COALESCE(Instrument_CoLD_ID, hop1_relations.Instrument_CoLD_ID)` | conditional |
| `Instrument Link` | `instrumentLink` | `instrument_link` | `hop1_relations.related_international_instruments[0].ncRecordId` | nested |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
