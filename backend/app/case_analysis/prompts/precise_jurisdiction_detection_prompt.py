PRECISE_JURISDICTION_DETECTION_PROMPT = """
You are a world-class legal expert specializing in identifying court jurisdictions from court decisions and legal documents.

Your task is to analyze the following court decision text and identify the PRECISE jurisdiction where this court decision was issued.

AVAILABLE JURISDICTIONS:
{jurisdiction_list}

ANALYSIS GUIDELINES:
Look for the following key indicators in the text:

1. **Court Names**:
   - Supreme courts, constitutional courts, high courts, appellate courts
   - Administrative courts, commercial courts, specialized tribunals
   - Federal vs. state/provincial court indicators

2. **Legal References**:
   - Specific statutes, codes, or legal frameworks cited
   - Constitutional provisions or articles referenced
   - Legal precedents or case law cited

3. **Geographic and Administrative Indicators**:
   - City names, regional references
   - Government departments or agencies mentioned
   - Administrative districts or legal divisions

4. **Language and Legal Terminology**:
   - Language of the decision (original language)
   - Legal terminology specific to certain legal systems
   - Citation formats and legal conventions

5. **Case Citation Format**:
   - How cases are cited and numbered
   - Court reporting systems used
   - Date formats and legal citation styles

RESPONSE REQUIREMENTS:
- Identify the EXACT jurisdiction name from the provided list
- If uncertain, choose the most likely match and indicate lower confidence
- If no clear jurisdiction can be determined, respond with "Unknown"
- Provide clear reasoning for your identification

Respond in the following format:
/"Jurisdiction/"

COURT DECISION TEXT:
{text}
"""
