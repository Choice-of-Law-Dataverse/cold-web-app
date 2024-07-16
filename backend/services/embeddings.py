import numpy as np
from mixedbread_ai.client import MixedbreadAI
from config import Config

class EmbeddingService:
    @staticmethod
    def get_embedding(text):
        mxbai = MixedbreadAI(api_key=Config.MIXEDBREAD_API_KEY)
        embedding = mxbai.embeddings(
            model="mixedbread-ai/mxbai-embed-large-v1",
            input=[text],
            normalized=True,
            encoding_format='ubinary',
            dimensions=512,
            truncation_strategy='start',
            prompt="Represent this sentence for searching relevant passages"
        )
        return np.array(embedding.data[0].embedding)
