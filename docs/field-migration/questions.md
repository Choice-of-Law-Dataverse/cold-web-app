# Questions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `Question` | `question` | `question` | `Question` | direct |
| `Question_Number` | `questionNumber` | `question_number` | `Question_Number` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Theme_Code` | `themeCode` | `theme_code` | `Primary_Theme` | direct |
| `Answering_Options` | `answeringOptions` | `answering_options` | `Answering_Options` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(updated_at, result_date)` | conditional |
| `Theme_Code` | `themeCode` | `theme_code` | `COALESCE(Primary_Theme, Theme_Code)` | conditional |
| `Themes` | `themes` | `themes` | `related_themes[*].Theme (joined by ', ')` | nested/array_join |
