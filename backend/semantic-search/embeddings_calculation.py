import psycopg2
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv
load_dotenv()

class DatabaseProcessor:
    def __init__(self, conn_params):
        self.conn_params = conn_params
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(**self.conn_params)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def fetch_data(self, query):
        df = pd.read_sql(query, self.conn)
        print(df.head())
        return df

    def concatenate_values(self, row):
        values = [str(val) for val in row if pd.notna(val) and val != "NA"]
        return ' '.join(values) if values else 'NA'

    def process_data(self, df):
        concatenated_strings = df.apply(self.concatenate_values, axis=1)
        embeddings = concatenated_strings.apply(self.mock_embedding)
        return embeddings

    def mock_embedding(self, text):
        # This function should return a numpy array of length 1024
        # For demonstration purposes, returning a dummy array
        return np.random.rand(64)

    # function to calculate vector embeddings for a given text
    def get_embedding(self, text):
        import numpy as np
        # LOCAL IMPLEMENTATION
        
        #from sentence_transformers import SentenceTransformer
        #from sentence_transformers.util import cos_sim
        #from sentence_transformers.quantization import quantize_embeddings

        # 1. Specify preffered dimensions
        #dimensions = 512
        # 2. load model
        #model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=dimensions)

        #embedding = model.encode(text)
        #return embedding

        
        # API IMPLEMENTATION
        
        from mixedbread_ai.client import MixedbreadAI
        
        mxbai = MixedbreadAI(api_key=os.getenv("MIXEDBREAD_API_KEY"))

        embedding = mxbai.embeddings(
            model="mixedbread-ai/mxbai-embed-large-v1",
            input=[text],
            normalized=True,
            encoding_format='ubinary',
            dimensions=512,
            truncation_strategy='start',
            prompt="Represent this sentence for searching relevant passages"
        )

        # convert embedding to np.array
        embedding = np.array(embedding.data[0].embedding)

        return embedding

    def add_embedding_column(self, table_name):
        self.cursor.execute(f"""
        ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS embedding vector(64);
        """)
        self.conn.commit()

    def update_embeddings(self, update_query, id_row1, id_row2, table_name, df, embeddings):
        for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc=f'Updating {table_name} embeddings'):
            embedding = embeddings[idx].tolist()  # Convert np.array to list
            self.cursor.execute(update_query, (embedding, row[id_row1], row[id_row2]))
        self.conn.commit()

    def process_table(self, update_query, id_row1, id_row2, select_query, table_name):
        df = self.fetch_data(select_query)
        embeddings = self.process_data(df)
        print(embeddings)
        print("Add embedding column if not exists")
        self.add_embedding_column(table_name)
        print("Added embedding column succesfully")
        print("Now updating embeddings")
        self.update_embeddings(update_query, id_row1, id_row2, table_name, df, embeddings)
        print("Successfully updated embeddings")

def main():
    conn_params = {
        'dbname': os.getenv("POSTGRES_AZURE_DBNAME"),
        'user': os.getenv("POSTGRES_AZURE_USER_ADMIN"),
        'password': os.getenv("POSTGRES_AZURE_PASSWORD_ADMIN"),
        'host': os.getenv("POSTGRES_AZURE_HOST"),
        'port': os.getenv("POSTGRES_AZURE_PORT")
    }

    db_processor = DatabaseProcessor(conn_params)
    db_processor.connect()

    try:
        answers_query = """
        SELECT 
            q.question, 
            a.answer, 
            a.open_text_field, 
            a.more_information, 
            j.jd_name AS jurisdiction
        FROM 
            answers a
        JOIN 
            questions q ON a.question = q.record_id
        JOIN 
            jurisdictions j ON a.jurisdiction = j.record_id;
        """
        update_answers_query = """
        UPDATE answers SET embedding = %s WHERE question = %s AND answer = %s;
        """
        db_processor.process_table(update_answers_query, 'question', 'answer', answers_query, 'answers')
        
        questions_query = """
        SELECT
            question,
            themes
        FROM
            questions;
        """
        update_questions_query= """
        UPDATE questions SET embedding = %s WHERE question = %s AND themes = %s;
        """
        db_processor.process_table(update_questions_query, 'question', 'themes', questions_query, 'questions')

        jurisdictions_query = """
        SELECT
            jurisdictions_id,
            jd_name,
            jd_type,
            region,
            north_south_divide
        FROM
            jurisdictions;
        """
        update_jurisdictions_query = """
        UPDATE jurisdictions SET embedding = %s WHERE jurisdictions_id = %s AND jd_name = %s;
        """
        db_processor.process_table(update_jurisdictions_query, 'jurisdictions_id', 'jd_name', jurisdictions_query, 'jurisdictions')

        legislations_query = """
        SELECT 
            l.title_english, 
            l.title_official,
            l.publication_date,
            l.entry_into_force,
            l.type_of_legislation,
            l.observations,
            COALESCE(STRING_AGG(j.jd_name, ', '), 'NA') AS jurisdiction
        FROM 
            legislations l
        LEFT JOIN 
            jurisdictionslegislations jl ON l.legislations_id = jl.legislations_id
        LEFT JOIN 
            jurisdictions j ON jl.jurisdictions_id = j.jurisdictions_id
        GROUP BY 
            l.legislations_id;
        """
        update_legislations_query = """
        UPDATE legislations SET embedding = %s WHERE title_english = %s AND title_official = %s;
        """
        db_processor.process_table(update_legislations_query, 'title_english', 'title_official', legislations_query, 'legislations')

        legal_provisions_query = """
        SELECT
            lp.article,
            lp.original_text,
            lp.english_text,
            COALESCE(STRING_AGG(l.title_english, ', '), 'NA') AS legislation,
            COALESCE(STRING_AGG(j.jd_name, ', '), 'NA') AS jurisdiction
        FROM
            legal_provisions lp
        LEFT JOIN
            legislationslegal_provisions llp ON lp.legal_provisions_id = llp.legal_provisions_id
        LEFT JOIN
            legislations l ON llp.legislations_id = l.legislations_id
        LEFT JOIN
            jurisdictionslegal_provisions jlp ON lp.legal_provisions_id = jlp.legal_provisions_id
        LEFT JOIN
            jurisdictions j ON jlp.jurisdictions_id = j.jurisdictions_id
        GROUP BY
            lp.legal_provisions_id;
        """
        update_legal_provisions_query = """
        UPDATE legal_provisions SET embedding = %s WHERE article = %s AND original_text = %s;
        """
        db_processor.process_table(update_legal_provisions_query, 'article', 'original_text', legal_provisions_query, 'legal_provisions')

        court_decisions_query = """
        SELECT
            cd.court_case,
            cd.abstract,
            cd.relevant_rules_of_law,
            cd.choice_of_law_issue,
            cd.court_position,
            cd.translated_excerpt,
            cd.legal_rules_used_by_court,
            cd.case_content,
            cd.additional_information,
            cd.observations,
            cd.case_quote,
            cd.relevant_facts,
            COALESCE(STRING_AGG(j.jd_name, ', '), 'NA') AS jurisdiction
        FROM
            court_decisions cd
        LEFT JOIN
            jurisdictionscourt_decisions jcd ON cd.court_decisions_id = jcd.court_decisions_id
        LEFT JOIN
            jurisdictions j ON jcd.jurisdictions_id = j.jurisdictions_id
        GROUP BY
            cd.court_decisions_id;
        """
        update_court_decisions_query = """
        UPDATE court_decisions SET embedding = %s WHERE court_case = %s AND abstract = %s;
        """
        db_processor.process_table(update_court_decisions_query, 'court_case', 'abstract', court_decisions_query, 'court_decisions')
    
    finally:
        db_processor.close()

if __name__ == "__main__":
    main()
