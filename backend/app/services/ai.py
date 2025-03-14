from app.config import Config
import requests


class GPT:
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY

    # Define the function that sends a request to OpenAI API
    def classify_user_query(self, user_query):
        # API endpoint
        url = "https://api.openai.com/v1/chat/completions"

        # Headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}",
        }

        # Data payload
        data = {
            "model": "ft:gpt-4o-mini-2024-07-18:personal:rag-categorisation-fine-tuning:AFerBLCp",
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Classify the following user query into one of the predefined categories and do not create new categories. Select from the following list:\nRevision/reform (concept)\nComparative method (concept)\nPersuasive authority (concept)\nRefer to an instrument (concept)\nParty autonomy (concept)\nRespect choice of law clause (concept)\nDépeçage (concept)\nModification of a choice of law clause (concept)\nConnection (concept)\nNeutral law / law of a 3rd country (concept)\nPIL codification (concept)\nConnection criteria/factors (concept)\nNon-State law / rules of law (concept)\nIncorporate rules by way of reference (concept)\nExpress choice (concept)\nTacit choice (concept)\nMandatory rules (concept)\nPublic policy (concept)\nArbitration (concept)\nArbitrators vs. State judges (concept)\nArbitral awards vs. court decisions (concept)\nInstitutional rules (arbitration) (concept)\nAbsence of choice (concept)\nWeaker/vulnerable parties (concept)\nInternational contracts (commercial) (concept)\nConventions/hard law (concept)\nPrinciples/soft law (concept)\nLegislation (concept)\nAbsence of choice (principle)\nPreamble (principle)\nParty autonomy (principle)\nFreedom of choice (principle)\nPartial choice (principle)\nDépeçage (principle)\nRules of law (principle)\nExpress and tacit choice (principle)\nMandatory rules (principle)\nPublic policy (principle)\nArbitration (principle)\nScope of the Principles (principle)\nFormal validity of the choice of law (principle)\nAgreement on the choice of law and battle of forms (principle)\nSeverability (principle)\nExclusion of renvoi (principle)\nScope of the chosen law (principle)\nAssignment (principle)\nEstablishment (principle)\nNo Category",
                        }
                    ],
                },
                {"role": "user", "content": [{"type": "text", "text": user_query}]},
            ],
            "temperature": 1,
            "max_tokens": 2048,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "response_format": {"type": "text"},
        }

        # Sending the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check if request was successful
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return {
                "error": f"Request failed with status code {response.status_code}",
                "details": response.text,
            }
