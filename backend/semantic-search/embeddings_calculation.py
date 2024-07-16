import numpy as np
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv
load_dotenv()
import time
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

class DatabaseProcessor:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.engine = None
        self.session = None

    def connect(self):
        self.engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={self.connection_string}")
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close(self):
        if self.session:
            self.session.close()

    def fetch_data(self, query):
        df = pd.read_sql(query, self.engine)
        print(df.head())
        return df

    def concatenate_values(self, row):
        values = [str(val) for val in row if pd.notna(val) and val != "NA"]
        return ' '.join(values) if values else 'NA'

    def process_data(self, df):
        concatenated_strings = df.apply(self.concatenate_values, axis=1)
        embeddings = concatenated_strings.apply(lambda text: self.mock_embedding(text)) # get_embedding_with_delay(text))
        return embeddings
    
    def get_embedding_with_delay(self, text):
        time.sleep(1)  # Wait for 1 second
        embedding = self.get_embedding_api(text)
        print(f"Processed embedding for text: {text[:50]}...")  # Show only first 50 chars for brevity
        return embedding

    def mock_embedding(self, text):
        # This function should return a numpy array of length 1024
        # For demonstration purposes, returning a dummy array
        return np.random.rand(64)

    def get_embedding_local(self, text):
        import numpy as np
        from sentence_transformers import SentenceTransformer

        # 1. Specify preferred dimensions
        dimensions = 512
        # 2. load model
        model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=dimensions)

        embedding = model.encode(text)

        # convert embedding to np.array
        return np.array(embedding)

    def get_embedding_api(self, text):
        import numpy as np
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

    def add_embedding_column(self, table_name, column_name='embedding', column_type='VARBINARY(MAX)'):
        if not self.engine:
            raise Exception("Database not connected. Call connect() before using this method.")
        
        inspector = sa.inspect(self.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]

        if column_name not in columns:
            with self.engine.connect() as connection:
                connection.execute(sa.text(f'ALTER TABLE {table_name} ADD {column_name} {column_type}'))
                print(f"Column '{column_name}' added to table '{table_name}'.")

    def update_embeddings(self, update_query, id_row1, id_row2, table_name, df, embeddings):
        with self.engine.connect() as conn:
            for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc=f'Updating {table_name} embeddings'):
                embedding = embeddings[idx].tobytes()  # Convert np.array to bytes
                conn.execute(
                    text(update_query),
                    {"embedding": embedding, "question": row[id_row1], "jurisdiction": row[id_row2]}
                )

    def process_table(self, update_query, id_row1, id_row2, select_query, table_name):
        df = self.fetch_data(select_query)
        embeddings = self.process_data(df)
        print(embeddings)
        print("Add embedding column if not exists")
        self.add_embedding_column(table_name)
        print("Added embedding column successfully")
        print("Now updating embeddings")
        self.update_embeddings(update_query, id_row1, id_row2, table_name, df, embeddings)
        print("Successfully updated embeddings")

def main():
    # record start time
    start = time.time()

    connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING_ADMIN")

    db_processor = DatabaseProcessor(connection_string)
    db_processor.connect()

    try:
        answers_query = """
        SELECT 
            [a].[fields.ID],
            [q].[fields.Question], 
            [a].[fields.Answer], 
            [a].[fields.Open text field], 
            [a].[fields.More information], 
            [j].[fields.Name] AS jurisdiction
        FROM 
            tbl3aGDFioDMVFCj1 AS a
        JOIN 
            tblDLXiRXUqdQKVRm AS q ON [a].[fields.Question] = [q].[fields.Record ID]
        JOIN 
            tbl3HFtHN0X1BR2o4 AS j ON [a].[fields.Jurisdiction] = [j].[fields.Record ID];
        """
        update_answers_query = """
        UPDATE tbl3aGDFioDMVFCj1
        SET embedding = :embedding
        WHERE [fields.Question] = (SELECT [fields.Record ID] FROM tblDLXiRXUqdQKVRm q WHERE q.[fields.Question] = :question)
        AND [fields.Jurisdiction] = (SELECT [fields.Record ID] FROM tbl3HFtHN0X1BR2o4 j WHERE j.[fields.Name] = :jurisdiction);
        """
        db_processor.process_table(update_answers_query, 'fields.Question', 'jurisdiction', answers_query, 'tbl3aGDFioDMVFCj1')

        legislations_query = """
        SELECT 
            l.[fields.Title (English translation)], 
            l.[fields.Official title],
            l.[fields.Publication date],
            l.[fields.Entry into force],
            l.[fields.Observations],
            COALESCE(STRING_AGG(j.[fields.Name], ', '), 'NA') AS jurisdiction
        FROM 
            tblOAXICRQjFFDUhh l
        OUTER APPLY (
            SELECT value AS jurisdictions_id
            FROM STRING_SPLIT([l].[fields.Jurisdictions], ',')
        ) AS split_jl
        LEFT JOIN 
            tbl3HFtHN0X1BR2o4 j ON split_jl.jurisdictions_id = j.ID
        GROUP BY
            l.[fields.Title (English translation)], 
            l.[fields.Official title],
            l.[fields.Publication date],
            l.[fields.Entry into force],
            l.[fields.Observations];
        """
        update_legislations_query = """
        UPDATE tblOAXICRQjFFDUhh SET embedding = :embedding WHERE [fields.Title (English translation)] = :title AND l.[fields.Official title] = :official_title;
        """
        db_processor.process_table(update_legislations_query, 'fields.Title (English translation)', 'fields.Official title', legislations_query, 'tblOAXICRQjFFDUhh')

        legal_provisions_query = """
        SELECT
            lp.[fields.Article],
            lp.[fields.Full text of the provision (Original language)],
            lp.[fields.Full text of the provision (English translation)],
            COALESCE(STRING_AGG(l.[fields.Title (English translation)], ', '), 'NA') AS legislation,
            COALESCE(STRING_AGG(j.[fields.Name], ', '), 'NA') AS jurisdiction
        FROM
            tbl9T17hyxLey2LG1 lp
        OUTER APPLY (
            SELECT value AS legislations_id
            FROM STRING_SPLIT([lp].[fields.Corresponding legislation], ',')
        ) AS split_llp
        LEFT JOIN
            tblOAXICRQjFFDUhh l ON split_llp.legislations_id = l.ID
        OUTER APPLY (
            SELECT value as jurisdictions_id
            FROM STRING_SPLIT([lp].[fields.Jurisdictions], ',')
        ) AS split_jlp
        LEFT JOIN
            tbl3HFtHN0X1BR2o4 j ON split_jlp.jurisdictions_id = j.ID
        GROUP BY
            lp.ID,
            lp.[fields.Article],
            lp.[fields.Full text of the provision (Original language)],
            lp.[fields.Full text of the provision (English translation)];
        """
        update_legal_provisions_query = """
        UPDATE tbl9T17hyxLey2LG1 SET embedding = :embedding WHERE [fields.Article] = :article AND [fields.Full text of the provision (Original language)] = :original_text;
        """
        db_processor.process_table(update_legal_provisions_query, 'fields.Article', 'fields.Full text of the provision (Original language)', legal_provisions_query, 'tbl9T17hyxLey2LG1')

        court_decisions_query = """
        SELECT
            [cd].[fields.Case],
            [cd].[fields.Abstract],
            [cd].[fields.Relevant rules of law involved],
            [cd].[fields.Choice of law issue],
            [cd].[fields.Court's position],
            [cd].[fields.Translated excerpt],
            [cd].[fields.Text of the relevant legal provisions],
            [cd].[fields.Content],
            [cd].[fields.Additional information],
            [cd].[fields.Observations],
            [cd].[fields.Quote],
            [cd].[fields.Relevant facts],
            COALESCE(STRING_AGG([j].[fields.Name], ', '), 'NA') AS jurisdictions
        FROM
            tbl8hWTY8ArXzJCr2 cd
        OUTER APPLY (
            SELECT value AS jurisdictions_id
            FROM STRING_SPLIT([cd].[fields.Jurisdictions], ',')
        ) AS split_jcd
        LEFT JOIN
            tbl3HFtHN0X1BR2o4 j ON split_jcd.[jurisdictions_id] = [j].[ID]
        GROUP BY
            [cd].[ID],
            [cd].[fields.Case],
            [cd].[fields.Abstract],
            [cd].[fields.Relevant rules of law involved],
            [cd].[fields.Choice of law issue],
            [cd].[fields.Court's position],
            [cd].[fields.Translated excerpt],
            [cd].[fields.Text of the relevant legal provisions],
            [cd].[fields.Content],
            [cd].[fields.Additional information],
            [cd].[fields.Observations],
            [cd].[fields.Quote],
            [cd].[fields.Relevant facts];
        """
        update_court_decisions_query = """
        UPDATE tbl8hWTY8ArXzJCr2 SET embedding = :embedding WHERE [fields.Case] = :case AND [fields.Abstract] = :abstract;
        """
        db_processor.process_table(update_court_decisions_query, 'fields.Case', 'fields.Abstract', court_decisions_query, 'tbl8hWTY8ArXzJCr2')

    finally:
        db_processor.close()
        # record end time
        end = time.time()
        
        # print the difference between start and end time in secs
        print("The time of execution of above program is :", (end-start), "sec")

if __name__ == "__main__":
    main()
