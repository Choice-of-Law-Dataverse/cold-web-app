# Jurisdictions -- Field Migration Reference

| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |
|---|---|---|---|---|
| `source_table` | `sourceTable` | `source_table` | `source_table (injected)` | base |
| `id` | `id` | `id` | `CoLD_ID` | base |
| `rank` | `rank` | `rank` | `rank (search score)` | base |
| `cold_id` | `coldId` | `cold_id` | `cold_id` | direct |
| `Name` | `name` | `name` | `Name` | direct |
| `Alpha-3 Code` | `alpha3Code` | `alpha_3_code` | `Alpha_3_Code` | direct |
| `Type` | `type` | `type` | `Type` | direct |
| `Region` | `region` | `region` | `Region` | direct |
| `North-South Divide` | `northSouthDivide` | `north_south_divide` | `North_South_Divide` | direct |
| `Jurisdictional Differentiator` | `jurisdictionalDifferentiator` | `jurisdictional_differentiator` | `Jurisdictional_Differentiator` | direct |
| `Record ID` | `recordId` | `record_id` | `ncRecordId` | direct |
| `Created` | `created` | `created` | `Created` | direct |
| `Last Modified` | `lastModified` | `last_modified` | `Last_Modified` | direct |
| `Last Modified By.id` | `lastModifiedById` | `last_modified_by_id` | `updated_by` | direct |
| `Created By.id` | `createdById` | `created_by_id` | `created_by` | direct |
| `Jurisdiction Summary` | `jurisdictionSummary` | `jurisdiction_summary` | `Jurisdiction_Summary` | direct |
| `Legal Family` | `legalFamily` | `legal_family` | `Legal_Family` | direct |
| `Answer Coverage` | `answerCoverage` | `answer_coverage` | `Answer_Coverage` | direct |
| `Irrelevant?` | `irrelevant` | `irrelevant` | `Irrelevant_ (boolean: True/False)` | boolean |
| `Done` | `done` | `done` | `Done (boolean: True/False)` | boolean |
