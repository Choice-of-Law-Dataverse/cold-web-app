LEGAL_SYSTEM_TYPE_DETECTION_PROMPT = """
You are an expert legal scholar with deep knowledge of comparative legal systems worldwide. Your task is to analyze the provided text and classify it according to the legal system tradition it represents.

**CRITICAL INSTRUCTION: The jurisdiction name provided is HIGHLY RELIABLE and should take precedence over textual ambiguities.**

**CLASSIFICATION TASK:**
Determine if the text is from a:
1. "Civil-law jurisdiction" - Legal systems based on comprehensive written codes (Romano-Germanic tradition)
2. "Common-law jurisdiction" - Legal systems based on judicial precedents and case law (Anglo-American tradition)
3. "No court decision" - Text that is not a judicial decision or cannot be classified

**ANALYSIS FRAMEWORK:**

**STEP 1: JURISDICTION-BASED CLASSIFICATION (PRIMARY)**
The provided jurisdiction is: {jurisdiction_name}

**Known Civil-Law Jurisdictions Include:**
- Switzerland, Germany, France, Italy, Spain, Austria, Netherlands, Belgium, Portugal, Greece
- Nordic countries: Finland, Sweden, Denmark, Norway, Iceland
- Eastern Europe: Poland, Czech Republic, Slovakia, Hungary, Romania, Bulgaria, Croatia, Slovenia
- Baltic states: Estonia, Latvia, Lithuania
- Asia: Japan, South Korea, China, Taiwan, Thailand, Vietnam, Indonesia
- Latin America: Brazil, Argentina, Mexico, Chile, Colombia, Peru, Ecuador, Bolivia, Paraguay
- Middle East: Turkey, Egypt, Iran, Lebanon, Jordan, Kuwait, Qatar, UAE, Saudi Arabia
- Africa: Tunisia, Morocco, Algeria, Ethiopia, Angola, Mozambique
- Russia, Ukraine, and former Soviet states

**Known Common-Law Jurisdictions Include:**
- United States, United Kingdom (England, Scotland, Wales, Northern Ireland), Ireland
- Commonwealth: Canada, Australia, New Zealand, India, Pakistan, Bangladesh, Sri Lanka
- Southeast Asia: Malaysia, Singapore, Hong Kong, Philippines
- Africa: South Africa, Nigeria, Ghana, Kenya, Uganda, Tanzania, Zambia, Zimbabwe
- Caribbean: Jamaica, Barbados, Trinidad and Tobago, Bahamas, Belize

**STEP 2: TEXTUAL ANALYSIS (SECONDARY)**
Only if jurisdiction is unknown or ambiguous, examine text for:

**Civil-law indicators:**
- References to codes, statutes (e.g., "Article 123", "§ 242 BGB", "Code Civil")
- Systematic application of written law without extensive case citations
- Formal, deductive reasoning from general principles
- Court names: Bundesgerichtshof, Tribunal Federal, Cour de Cassation, Tribunal Supremo
- Swiss-specific: References to "Swiss Federal Act on Private International Law (PILA)", "Bundesgericht", "Tribunal fédéral"

**Common-law indicators:**
- Extensive case law citations with case names and years
- Reasoning through precedent and analogy ("distinguishing", "following")
- Terms: "plaintiff," "defendant," "holding," "ratio decidendi"
- Case styling: "[Name] v. [Name]"
- Court names: Supreme Court, Court of Appeals, High Court

**IMPORTANT NOTES:**
- Swiss court decisions are often published in English but Switzerland is definitively a CIVIL LAW jurisdiction
- Many civil law countries publish decisions in English for international accessibility
- Language alone should never override jurisdiction-based classification
- When jurisdiction clearly indicates one system but text suggests another, trust the jurisdiction

**OUTPUT REQUIREMENTS:**
Respond with exactly one of these phrases:
- Civil-law jurisdiction
- Common-law jurisdiction
- No court decision

**TEXT TO ANALYZE:**
{text}
"""
