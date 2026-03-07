# Regional Instruments -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `ID Number` | `idNumber` | `id_number` | `ID_Number` | direct |
| `Title` | `title` | `title` | `Title` | direct |
| `Abbreviation` | `abbreviation` | `abbreviation` | `Abbreviation` | direct |
| `Date` | `date` | `date` | `Date` | direct |
| `URL` | `url` | `url` | `URL` | direct |
| `Attachment` | `attachment` | `attachment` | `Attachment` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `updated_at` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `sort_date` | `sortDate` | `sort_date` | `COALESCE(Date, updated_at)` | conditional |
| `Specialists` | `specialists` | `specialists` | `related_specialists[*].Specialist (joined by ',')` | nested/array_join |
| `Specialists Link` | `specialistsLink` | `specialists_link` | `related_specialists[*].ncRecordId (joined by ',')` | nested/array_join |
| `Regional Legal Provisions` | `regionalLegalProvisions` | `regional_legal_provisions` | `related_legal_provisions[*].CoLD_ID (joined by ',')` | nested/array_join |
| `Regional Legal Provisions Link` | `regionalLegalProvisionsLink` | `regional_legal_provisions_link` | `related_legal_provisions[*].ncRecordId (joined by ',')` | nested/array_join |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by.id` | user |
| `Last Modified By.email` | `lastModifiedByEmail` | `last_modified_by_email` | `updated_by.email` | user |
| `Last Modified By.name` | `lastModifiedByName` | `last_modified_by_name` | `updated_by.name` | user |
| `Created By.id` | `createdById` | `created_by_id` | `created_by.id` | user |
| `Created By.email` | `createdByEmail` | `created_by_email` | `created_by.email` | user |
| `Created By.name` | `createdByName` | `created_by_name` | `created_by.name` | user |
