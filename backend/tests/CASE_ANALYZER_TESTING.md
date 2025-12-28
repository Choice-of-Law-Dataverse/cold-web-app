# Case Analyzer Insertion Testing Guide

## Overview
This guide describes how to test the automatic insertion of case_analyzer suggestions into the Court_Decisions table.

## Prerequisites
- Access to the moderation UI at `/moderation`
- At least one case_analyzer suggestion in pending state
- Database access to verify records

## Test Steps

### 1. View Pending Case Analyzer Suggestions
1. Navigate to `/moderation/case-analyzer`
2. Verify that pending suggestions are displayed with:
   - Case citation
   - Jurisdiction
   - Theme
   - Date
   - Submitter information

### 2. View Suggestion Detail
1. Click on a specific case analyzer suggestion
2. Verify the detail view shows:
   - All normalized fields (Username, E-Mail, Model, Date, Case Citation, Jurisdiction, etc.)
   - "Mark as finished" button
   - "Reject" button

### 3. Approve a Case Analyzer Suggestion
1. Click the "Mark as finished" button
2. Verify redirection back to the list page
3. Verify the suggestion is no longer in the pending list

### 4. Verify Database Insertion
Query the Court_Decisions table to verify the new record:

```sql
SELECT 
    id,
    "Case_Citation",
    "Date_of_Judgment",
    "Abstract",
    "Relevant_Facts",
    "PIL_Provisions",
    "Choice_of_Law_Issue",
    "Court_s_Position",
    "Internal_Notes"
FROM nc_p1q5."Court_Decisions"
WHERE id = <merged_id>;
```

Expected results:
- All core fields from the case analyzer are populated
- Internal_Notes contains metadata:
  - Jurisdiction Type
  - Choice of Law Section(s)
  - Theme
  - AI Model

### 5. Verify Jurisdiction Linking
Query the jurisdiction link table:

```sql
SELECT 
    cd."Case_Citation",
    j."Name"
FROM nc_p1q5."Court_Decisions" cd
JOIN nc_p1q5."_nc_m2m_Jurisdictions_Court_Decisions" link 
    ON cd.id = link."Court_Decisions_id"
JOIN nc_p1q5."Jurisdictions" j 
    ON link."Jurisdictions_id" = j.id
WHERE cd.id = <merged_id>;
```

Expected: The jurisdiction from the case analyzer is properly linked.

### 6. Verify Suggestion Status
Query the suggestions table to verify the approval:

```sql
SELECT 
    id,
    data->>'moderation_status' as status,
    data->>'moderated_by' as moderator,
    data->>'merged_record_id' as merged_id
FROM suggestions_case_analyzer
WHERE id = <suggestion_id>;
```

Expected:
- status = 'approved'
- merged_id = the Court_Decisions record ID

## Test Cases

### Test Case 1: Complete Case Analyzer Data
- Use a suggestion with all fields populated
- Verify all fields are correctly mapped to Court_Decisions

### Test Case 2: Minimal Case Analyzer Data
- Use a suggestion with only required fields (case_citation)
- Verify the record is created with available data
- Verify empty fields are not causing errors

### Test Case 3: Jurisdiction Linking
- Use a suggestion with a valid jurisdiction (e.g., "United Kingdom", "Germany")
- Verify jurisdiction is properly linked via m2m table

### Test Case 4: Multiple Metadata Fields
- Use a suggestion with jurisdiction_type, theme, choice_of_law_sections
- Verify all metadata is combined in Internal_Notes

### Test Case 5: Rejection Flow
- Click "Reject" instead of "Mark as finished"
- Verify suggestion is marked as rejected
- Verify NO Court_Decisions record is created

## Expected Behavior vs Previous Behavior

### Before this change:
- User had to:
  1. View the case analyzer suggestion
  2. Copy the raw JSON data
  3. Manually parse the JSON
  4. Manually create a Court_Decisions record in NocoDB
  5. Manually link jurisdictions
  6. Mark the suggestion as approved

### After this change:
- User only needs to:
  1. View the case analyzer suggestion
  2. Click "Mark as finished"
  3. System automatically creates Court_Decisions record with all data

## Rollback Plan
If issues are found:
1. Revert the changes to `app/routes/moderation.py` and `app/services/moderation_writer.py`
2. The suggestion records remain intact
3. Previously created Court_Decisions records remain intact

## Known Limitations
1. The Internal_Notes field combines multiple metadata fields - if more granular storage is needed, schema changes would be required
2. Jurisdiction linking relies on string matching - if the jurisdiction name doesn't match, linking may fail (but record is still created)
3. Date parsing depends on the format from the case analyzer - unexpected formats may need handling
