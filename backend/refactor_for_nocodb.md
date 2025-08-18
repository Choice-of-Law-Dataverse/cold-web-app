# Documentation to switch from old Airtable --> Postgres logic to NocoDB running on Postgres

I have developed a full stack system which used to work like so: Airtable as the main data management center. The following python application to move the data from Airtable to a designated postgres database:

main.py:
```
from config import AIRTABLE_API_KEY, AZURE_SQL_CONNECTION_STRING, AIRTABLE_BASE_ID
from services.airtable_service import AirtableService
from services.sql_service import SQLService
from services.data_processor import process_list_like_values


def main():
    airtable_service = AirtableService(AIRTABLE_API_KEY, AIRTABLE_BASE_ID)
    sql_service = SQLService(AZURE_SQL_CONNECTION_STRING)

    table_names = airtable_service.fetch_table_names()

    for table_id, table_name in table_names.items():
        print(f"Processing table: {table_name}")
        df = airtable_service.fetch_data(table_id)
        df = process_list_like_values(df)
        sql_service.create_table(df, table_name)
        sql_service.push_data(df, table_name)

    sql_service.add_full_text_search()


if __name__ == "__main__":
    main()
```

services/airtable_service.py:
```
import pandas as pd
from pyairtable import Api
from .data_processor import remove_fields_prefix


class AirtableService:
    def __init__(self, api_key, base_id):
        self.api = Api(api_key)
        self.base_id = base_id

    def fetch_data(self, table_id):
        table = self.api.table(self.base_id, table_id)
        records = table.all()

        if records:
            df = pd.json_normalize(
                [record["fields"] for record in records]
            )  # Directly normalize 'fields'
            df = remove_fields_prefix(df)
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no records

    def fetch_table_names(self):
        base_meta = self.api.base(self.base_id).tables()
        return {table.id: table.name for table in base_meta}
```

services/sql_service.py:
```
from sqlalchemy import create_engine, text, exc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.url import make_url
from config import AZURE_SQL_CONNECTION_STRING


class SQLService:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.connection_string = connection_string

    def create_table(self, df, table_name):
        """
        Create a table in the database based on the dataframe's schema.
        """
        dtype_map = {
            "int64": "BIGINT",
            "float64": "DOUBLE PRECISION",
            "datetime64[ns]": "TIMESTAMP",
            "object": "TEXT",
        }
        columns = []
        for column, dtype in df.dtypes.items():
            sql_dtype = dtype_map.get(
                str(dtype), "NVARCHAR(MAX)"
            )  # Map dtypes to SQL-compatible types
            columns.append(f'"{column}" {sql_dtype}')
        columns_sql = ", ".join(columns)
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql})'
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                print(f"Table '{table_name}' created successfully.")
        except SQLAlchemyError as e:
            print(f"An error occurred while creating the table {table_name}: {str(e)}")

    def push_data(self, df, table_name):
        try:
            df.to_sql(table_name, con=self.engine, if_exists="append", index=False)
            print(f"Data pushed to table '{table_name}' successfully.")
        except SQLAlchemyError as e:
            print(
                f"An error occurred while pushing data to table {table_name}: {str(e)}"
            )

    def add_full_text_search(self):
        try:
            with self.engine.begin() as conn:
                # Check and create full-text search column and index for "Answers" table
                conn.execute(
                    text(
                        """
                    -- Ensure that the column doesn't already exist before adding it
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'Answers' 
                                       AND column_name = 'search') THEN
                            -- Add the search tsvector column for "Answers" table
                            ALTER TABLE "Answers"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Question", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Jurisdictions", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("More Information", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Themes", '')), 'C')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'Answers'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "Answers" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                    
                    -- Populate sort_date column for "Answers" table
                    UPDATE "Answers" 
                    SET sort_date = CASE 
                        WHEN "Last Modified" IS NOT NULL THEN 
                            to_date(substring("Last Modified", 1, 10), 'YYYY-MM-DD')
                        ELSE NULL 
                    END 
                    WHERE sort_date IS NULL;
                    
                    -- Create the GIN index for full-text search on "Answers" table
                    CREATE INDEX IF NOT EXISTS idx_search_as ON "Answers" USING GIN(search);
                """
                    )
                )
                print("Full-text search setup completed for 'Answers' table.")

                # Check and create full-text search column and index for "HCCH Answers" table
                conn.execute(
                    text(
                        """
                    -- Ensure that the column doesn't already exist before adding it
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'HCCH Answers' 
                                       AND column_name = 'search') THEN
                            -- Add the search tsvector column for "HCCH Answers" table
                            ALTER TABLE "HCCH Answers"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Adapted Question", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("International Instruments", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Themes", '')), 'B')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'HCCH Answers'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "HCCH Answers" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                    
                    -- Populate sort_date column for "HCCH Answers" table
                    UPDATE "HCCH Answers" 
                    SET sort_date = CASE 
                        WHEN "Last Modified" IS NOT NULL THEN 
                            to_date(substring("Last Modified", 1, 10), 'YYYY-MM-DD')
                        ELSE NULL 
                    END 
                    WHERE sort_date IS NULL;
                    
                    -- Create the GIN index for full-text search on "HCCH Answers" table
                    CREATE INDEX IF NOT EXISTS idx_search_hcch_as ON "HCCH Answers" USING GIN(search); -- Renamed index to be unique
                """
                    )
                )
                print("Full-text search setup completed for 'HCCH Answers' table.")

                # Check and create full-text search column and index for "Court Decisions" table
                conn.execute(
                    text(
                        """
                    -- Ensure that the column doesn't already exist before adding it
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'Court Decisions' 
                                       AND column_name = 'search') THEN
                            -- Add the search tsvector column for "Court Decisions" table
                            ALTER TABLE "Court Decisions"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Case Citation", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Jurisdictions", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("English Translation", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Answers Question", '')), 'C')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'Court Decisions'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "Court Decisions" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                    
                    -- Populate sort_date column for "Court Decisions" table
                    UPDATE "Court Decisions" 
                    SET sort_date = CASE
                        WHEN "Date" ~ '^\\d{4}$' THEN to_date(COALESCE("Date", '1900'), 'YYYY')
                        WHEN "Date" ~ '^\\d{2}\\.\\d{2}\\.\\d{4}$' THEN to_date(COALESCE("Date", '01.01.1900'), 'DD.MM.YYYY')
                        ELSE NULL
                    END 
                    WHERE sort_date IS NULL;
                    
                    -- Create the GIN index for full-text search on "Court Decisions" table
                    CREATE INDEX IF NOT EXISTS idx_search_cds ON "Court Decisions" USING GIN(search);
                """
                    )
                )
                print("Full-text search setup completed for 'Court Decisions' table.")

                # Check and create full-text search column and index for "Domestic Instruments" table
                conn.execute(
                    text(
                        """
                    -- Ensure that the column doesn't already exist before adding it
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'Domestic Instruments' 
                                       AND column_name = 'search') THEN
                            -- Add the search tsvector column for "Domestic Instruments" table
                            ALTER TABLE "Domestic Instruments"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Title (in English)", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Official Title", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Jurisdictions", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Publication Date", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Entry Into Force", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Full Text of the Provisions", '')), 'C') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Domestic Legal Provisions Full Text of the Provision (Original Language)", '')), 'C') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Domestic Legal Provisions Full Text of the Provision (English Translation)", '')), 'C')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'Domestic Instruments'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "Domestic Instruments" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                      -- Populate sort_date column for "Domestic Instruments" table
                    UPDATE "Domestic Instruments" 
                    SET sort_date = CASE
                        WHEN "Date" ~ '^\\d{4}$' THEN to_date(COALESCE("Date", '1900'), 'YYYY')
                        ELSE NULL
                    END 
                    WHERE sort_date IS NULL;
                    
                    -- Create the GIN index for full-text search on "Domestic Instruments" table
                    CREATE INDEX IF NOT EXISTS idx_search_di ON "Domestic Instruments" USING GIN(search); -- Renamed index to be unique
                """
                    )
                )
                print(
                    "Full-text search setup completed for 'Domestic Instruments' table."
                )

                # Check and create full-text search column and index for "Regional Instruments" table
                conn.execute(
                    text(
                        """
                    -- Ensure that the column doesn't already exist before adding it
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'Regional Instruments' 
                                       AND column_name = 'search') THEN
                            -- Add the search tsvector column for "Regional Instruments" table
                            ALTER TABLE "Regional Instruments"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Abbreviation", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Title", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Specialists", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Date", '')), 'C')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'Regional Instruments'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "Regional Instruments" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                      -- Populate sort_date column for "Regional Instruments" table
                    UPDATE "Regional Instruments" 
                    SET sort_date = CASE
                        WHEN "Date" ~ '^\\d{4}-\\d{2}-\\d{2}$' THEN to_date(COALESCE("Date", '1900-01-01'), 'YYYY-MM-DD')
                        ELSE NULL
                    END 
                    WHERE sort_date IS NULL;
                    
                    -- Create the GIN index for full-text search on "Regional Instruments" table
                    CREATE INDEX IF NOT EXISTS idx_search_ri ON "Regional Instruments" USING GIN(search); -- Renamed index to be unique
                """
                    )
                )
                print(
                    "Full-text search setup completed for 'Regional Instruments' table."
                )

                # Check and create full-text search column and index for "International Instruments" table
                conn.execute(
                    text(
                        """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'International Instruments' 
                                       AND column_name = 'search') THEN
                            ALTER TABLE "International Instruments"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Name", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Specialists", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Date", '')), 'C')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'International Instruments'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "International Instruments" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                      -- Populate sort_date column for "International Instruments" table
                    UPDATE "International Instruments" 
                    SET sort_date = CASE
                        WHEN "Date" ~ '^\\d{4}-\\d{2}-\\d{2}$' THEN to_date(COALESCE("Date", '1900-01-01'), 'YYYY-MM-DD')
                        ELSE NULL
                    END 
                    WHERE sort_date IS NULL;
                    
                    CREATE INDEX IF NOT EXISTS idx_search_ii ON "International Instruments" USING GIN(search); -- Renamed index to be unique
                """
                    )
                )
                print(
                    "Full-text search setup completed for 'International Instruments' table."
                )

                # Check and create full-text search column and index for "Literature" table
                conn.execute(
                    text(
                        """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                       WHERE table_name = 'Literature' 
                                       AND column_name = 'search') THEN
                            ALTER TABLE "Literature"
                            ADD COLUMN search tsvector
                            GENERATED ALWAYS AS (
                              setweight(to_tsvector('english', COALESCE("Title", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Author", '')), 'A') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Publication Title", '')), 'B') || ' ' ||
                              setweight(to_tsvector('english', COALESCE("Publication Year"::text, '')), 'C')
                            ) STORED;
                        END IF;                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                       WHERE table_name = 'Literature'
                                       AND column_name = 'sort_date') THEN
                            ALTER TABLE "Literature" ADD COLUMN sort_date DATE;
                        END IF;                    END $$;
                    
                    -- Populate sort_date column for "Literature" table
                    UPDATE "Literature" 
                    SET sort_date = CASE
                        WHEN "Publication Year"::text ~ '^\\d{4}$' THEN to_date(COALESCE("Publication Year"::text, '1900'), 'YYYY')
                        ELSE NULL
                    END 
                    WHERE sort_date IS NULL;
                    
                    CREATE INDEX IF NOT EXISTS idx_search_lit ON "Literature" USING GIN(search); -- Renamed index to be unique
                """
                    )
                )
                print("Full-text search setup completed for 'Literature' table.")

        except SQLAlchemyError as e:
            print(f"An error occurred during full-text search setup: {str(e)}")
```

The postgres database would then feed into a fastapi backend which would serve a nuxt frontend. I have now migrated Airtable to NocoDB and would like to use the NocoDB postgres database directly to feed into the fastapi backend. How do I best approach the changes I need to make in fastapi?


Schema of the old Postgres database created with the previous python scripts:

|table_full_name                      |column_name                                                    |ordinal_position|data_type       |is_nullable|column_default|
|-------------------------------------|---------------------------------------------------------------|----------------|----------------|-----------|--------------|
|public.Abbreviations                 |Abbreviation                                                   |1               |text            |YES        |NULL          |
|public.Abbreviations                 |Designation                                                    |2               |text            |YES        |NULL          |
|public.Abbreviations                 |Type                                                           |3               |text            |YES        |NULL          |
|public.Abbreviations                 |Last Modified                                                  |4               |text            |YES        |NULL          |
|public.Abbreviations                 |Created                                                        |5               |text            |YES        |NULL          |
|public.Abbreviations                 |Last Modified By.id                                            |6               |text            |YES        |NULL          |
|public.Abbreviations                 |Last Modified By.email                                         |7               |text            |YES        |NULL          |
|public.Abbreviations                 |Last Modified By.name                                          |8               |text            |YES        |NULL          |
|public.Abbreviations                 |Created By.id                                                  |9               |text            |YES        |NULL          |
|public.Abbreviations                 |Created By.email                                               |10              |text            |YES        |NULL          |
|public.Abbreviations                 |Created By.name                                                |11              |text            |YES        |NULL          |
|public.Answers                       |ID                                                             |1               |text            |YES        |NULL          |
|public.Answers                       |Question Link                                                  |2               |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions Link                                             |3               |text            |YES        |NULL          |
|public.Answers                       |Question                                                       |4               |text            |YES        |NULL          |
|public.Answers                       |Questions Theme Code                                           |5               |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions Alpha-3 code                                     |6               |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions                                                  |7               |text            |YES        |NULL          |
|public.Answers                       |Answer                                                         |8               |text            |YES        |NULL          |
|public.Answers                       |Record ID                                                      |9               |text            |YES        |NULL          |
|public.Answers                       |Created                                                        |10              |text            |YES        |NULL          |
|public.Answers                       |Themes                                                         |11              |text            |YES        |NULL          |
|public.Answers                       |Last Modified                                                  |12              |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions Literature Title                                 |13              |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions Literature ID                                    |14              |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions Region                                           |15              |text            |YES        |NULL          |
|public.Answers                       |Jurisdictions Irrelevant                                       |16              |text            |YES        |NULL          |
|public.Answers                       |Number                                                         |17              |text            |YES        |NULL          |
|public.Answers                       |Literature                                                     |18              |text            |YES        |NULL          |
|public.Answers                       |Last Modified By.id                                            |19              |text            |YES        |NULL          |
|public.Answers                       |Last Modified By.email                                         |20              |text            |YES        |NULL          |
|public.Answers                       |Last Modified By.name                                          |21              |text            |YES        |NULL          |
|public.Answers                       |Created By.id                                                  |22              |text            |YES        |NULL          |
|public.Answers                       |Created By.email                                               |23              |text            |YES        |NULL          |
|public.Answers                       |Created By.name                                                |24              |text            |YES        |NULL          |
|public.Answers                       |Domestic Instruments Link                                      |25              |text            |YES        |NULL          |
|public.Answers                       |Domestic Legal Provisions Link                                 |26              |text            |YES        |NULL          |
|public.Answers                       |Domestic Legal Provisions                                      |27              |text            |YES        |NULL          |
|public.Answers                       |Domestic Instruments                                           |28              |text            |YES        |NULL          |
|public.Answers                       |Domestic Instruments ID                                        |29              |text            |YES        |NULL          |
|public.Answers                       |Court Decisions Link                                           |30              |text            |YES        |NULL          |
|public.Answers                       |Court Decisions                                                |31              |text            |YES        |NULL          |
|public.Answers                       |Court Decisions ID                                             |32              |text            |YES        |NULL          |
|public.Answers                       |More Information                                               |33              |text            |YES        |NULL          |
|public.Answers                       |To Review?                                                     |34              |boolean         |YES        |NULL          |
|public.Answers                       |OUP Book Quote                                                 |35              |text            |YES        |NULL          |
|public.Answers                       |Interesting Answer                                             |36              |double precision|YES        |NULL          |
|public.Answers                       |Literature Link                                                |37              |text            |YES        |NULL          |
|public.Answers                       |Secondary Domestic Legal Provisions Link                       |38              |text            |YES        |NULL          |
|public.Answers                       |Secondary Legal Provision Articles                             |39              |text            |YES        |NULL          |
|public.Answers                       |search                                                         |40              |tsvector        |YES        |NULL          |
|public.Answers                       |sort_date                                                      |41              |date            |YES        |NULL          |
|public.Arbitral Awards               |Case Number                                                    |1               |text            |YES        |NULL          |
|public.Arbitral Awards               |Context                                                        |2               |text            |YES        |NULL          |
|public.Arbitral Awards               |Arbitral Institution Link                                      |3               |text            |YES        |NULL          |
|public.Arbitral Awards               |Award Summary                                                  |4               |text            |YES        |NULL          |
|public.Arbitral Awards               |Year                                                           |5               |double precision|YES        |NULL          |
|public.Arbitral Awards               |Nature of the Award                                            |6               |text            |YES        |NULL          |
|public.Arbitral Awards               |Seat (Town)                                                    |7               |text            |YES        |NULL          |
|public.Arbitral Awards               |Source                                                         |8               |text            |YES        |NULL          |
|public.Arbitral Awards               |Record ID                                                      |9               |text            |YES        |NULL          |
|public.Arbitral Awards               |Last Modified                                                  |10              |text            |YES        |NULL          |
|public.Arbitral Awards               |ID Number                                                      |11              |bigint          |YES        |NULL          |
|public.Arbitral Awards               |Themes Link                                                    |12              |text            |YES        |NULL          |
|public.Arbitral Awards               |Created                                                        |13              |text            |YES        |NULL          |
|public.Arbitral Awards               |Last Modified By.id                                            |14              |text            |YES        |NULL          |
|public.Arbitral Awards               |Last Modified By.email                                         |15              |text            |YES        |NULL          |
|public.Arbitral Awards               |Last Modified By.name                                          |16              |text            |YES        |NULL          |
|public.Arbitral Awards               |Created By.id                                                  |17              |text            |YES        |NULL          |
|public.Arbitral Awards               |Created By.email                                               |18              |text            |YES        |NULL          |
|public.Arbitral Awards               |Created By.name                                                |19              |text            |YES        |NULL          |
|public.Arbitral Awards               |Jurisdictions Link                                             |20              |text            |YES        |NULL          |
|public.Arbitral Institutions         |Institution                                                    |1               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Abbreviation                                                   |2               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Arbitral Awards Link                                           |3               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Arbitral Rules Link                                            |4               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Jurisdictions Link                                             |5               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Record ID                                                      |6               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Last Modified                                                  |7               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Created                                                        |8               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Last Modified By.id                                            |9               |text            |YES        |NULL          |
|public.Arbitral Institutions         |Last Modified By.email                                         |10              |text            |YES        |NULL          |
|public.Arbitral Institutions         |Last Modified By.name                                          |11              |text            |YES        |NULL          |
|public.Arbitral Institutions         |Created By.id                                                  |12              |text            |YES        |NULL          |
|public.Arbitral Institutions         |Created By.email                                               |13              |text            |YES        |NULL          |
|public.Arbitral Institutions         |Created By.name                                                |14              |text            |YES        |NULL          |
|public.Arbitral Rules                |Set of Rules                                                   |1               |text            |YES        |NULL          |
|public.Arbitral Rules                |Arbitral Institutions Link                                     |2               |text            |YES        |NULL          |
|public.Arbitral Rules                |In Force From                                                  |3               |text            |YES        |NULL          |
|public.Arbitral Rules                |Official Source (URL)                                          |4               |text            |YES        |NULL          |
|public.Arbitral Rules                |Record ID                                                      |5               |text            |YES        |NULL          |
|public.Arbitral Rules                |Last Modified                                                  |6               |text            |YES        |NULL          |
|public.Arbitral Rules                |Created                                                        |7               |text            |YES        |NULL          |
|public.Arbitral Rules                |Last Modified By.id                                            |8               |text            |YES        |NULL          |
|public.Arbitral Rules                |Last Modified By.email                                         |9               |text            |YES        |NULL          |
|public.Arbitral Rules                |Last Modified By.name                                          |10              |text            |YES        |NULL          |
|public.Arbitral Rules                |Created By.id                                                  |11              |text            |YES        |NULL          |
|public.Arbitral Rules                |Created By.email                                               |12              |text            |YES        |NULL          |
|public.Arbitral Rules                |Created By.name                                                |13              |text            |YES        |NULL          |
|public.Court Decisions               |Case Citation                                                  |1               |text            |YES        |NULL          |
|public.Court Decisions               |Jurisdictions Link                                             |2               |text            |YES        |NULL          |
|public.Court Decisions               |Internal Notes                                                 |3               |text            |YES        |NULL          |
|public.Court Decisions               |Themes                                                         |4               |text            |YES        |NULL          |
|public.Court Decisions               |Record ID                                                      |5               |text            |YES        |NULL          |
|public.Court Decisions               |ID-number                                                      |6               |bigint          |YES        |NULL          |
|public.Court Decisions               |ID                                                             |7               |text            |YES        |NULL          |
|public.Court Decisions               |Case Rank                                                      |8               |double precision|YES        |NULL          |
|public.Court Decisions               |Jurisdictions                                                  |9               |text            |YES        |NULL          |
|public.Court Decisions               |Region (from Jurisdictions)                                    |10              |text            |YES        |NULL          |
|public.Court Decisions               |Created                                                        |11              |text            |YES        |NULL          |
|public.Court Decisions               |Date                                                           |12              |text            |YES        |NULL          |
|public.Court Decisions               |Case Title                                                     |13              |text            |YES        |NULL          |
|public.Court Decisions               |Instance                                                       |14              |text            |YES        |NULL          |
|public.Court Decisions               |Last Modified                                                  |15              |text            |YES        |NULL          |
|public.Court Decisions               |Jurisdictions Alpha-3 Code                                     |16              |text            |YES        |NULL          |
|public.Court Decisions               |Publication Date ISO                                           |17              |text            |YES        |NULL          |
|public.Court Decisions               |Created time                                                   |18              |text            |YES        |NULL          |
|public.Court Decisions               |Questions                                                      |19              |text            |YES        |NULL          |
|public.Court Decisions               |Domestic Legal Provisions                                      |20              |text            |YES        |NULL          |
|public.Court Decisions               |Last Modified By.id                                            |21              |text            |YES        |NULL          |
|public.Court Decisions               |Last Modified By.email                                         |22              |text            |YES        |NULL          |
|public.Court Decisions               |Last Modified By.name                                          |23              |text            |YES        |NULL          |
|public.Court Decisions               |Added By.id                                                    |24              |text            |YES        |NULL          |
|public.Court Decisions               |Added By.email                                                 |25              |text            |YES        |NULL          |
|public.Court Decisions               |Added By.name                                                  |26              |text            |YES        |NULL          |
|public.Court Decisions               |Created By.id                                                  |27              |text            |YES        |NULL          |
|public.Court Decisions               |Created By.email                                               |28              |text            |YES        |NULL          |
|public.Court Decisions               |Created By.name                                                |29              |text            |YES        |NULL          |
|public.Court Decisions               |Answers Link                                                   |30              |text            |YES        |NULL          |
|public.Court Decisions               |Answers Question                                               |31              |text            |YES        |NULL          |
|public.Court Decisions               |Official Source (URL)                                          |32              |text            |YES        |NULL          |
|public.Court Decisions               |Official Source (PDF)                                          |33              |text            |YES        |NULL          |
|public.Court Decisions               |Abstract                                                       |34              |text            |YES        |NULL          |
|public.Court Decisions               |English Translation                                            |35              |text            |YES        |NULL          |
|public.Court Decisions               |Choice of Law Issue                                            |36              |text            |YES        |NULL          |
|public.Court Decisions               |Court's Position                                               |37              |text            |YES        |NULL          |
|public.Court Decisions               |Text of the Relevant Legal Provisions                          |38              |text            |YES        |NULL          |
|public.Court Decisions               |Translated Excerpt                                             |39              |text            |YES        |NULL          |
|public.Court Decisions               |Questions Link                                                 |40              |text            |YES        |NULL          |
|public.Court Decisions               |Quote                                                          |41              |text            |YES        |NULL          |
|public.Court Decisions               |Relevant Facts                                                 |42              |text            |YES        |NULL          |
|public.Court Decisions               |Date of Judgment                                               |43              |text            |YES        |NULL          |
|public.Court Decisions               |PIL Provisions                                                 |44              |text            |YES        |NULL          |
|public.Court Decisions               |Original Text                                                  |45              |text            |YES        |NULL          |
|public.Court Decisions               |Domestic Legal Provisions Link                                 |46              |text            |YES        |NULL          |
|public.Court Decisions               |Copyright Issues                                               |47              |boolean         |YES        |NULL          |
|public.Court Decisions               |search                                                         |48              |tsvector        |YES        |NULL          |
|public.Court Decisions               |sort_date                                                      |49              |date            |YES        |NULL          |
|public.Domestic Instruments          |Title (in English)                                             |1               |text            |YES        |NULL          |
|public.Domestic Instruments          |Jurisdictions Link                                             |2               |text            |YES        |NULL          |
|public.Domestic Instruments          |Type (from Jurisdictions)                                      |3               |text            |YES        |NULL          |
|public.Domestic Instruments          |Answers Link                                                   |4               |text            |YES        |NULL          |
|public.Domestic Instruments          |Relevant Provisions                                            |5               |text            |YES        |NULL          |
|public.Domestic Instruments          |Question ID                                                    |6               |text            |YES        |NULL          |
|public.Domestic Instruments          |Source (URL)                                                   |7               |text            |YES        |NULL          |
|public.Domestic Instruments          |Source (PDF)                                                   |8               |text            |YES        |NULL          |
|public.Domestic Instruments          |Record ID                                                      |9               |text            |YES        |NULL          |
|public.Domestic Instruments          |ID                                                             |10              |text            |YES        |NULL          |
|public.Domestic Instruments          |ID-number                                                      |11              |bigint          |YES        |NULL          |
|public.Domestic Instruments          |Jurisdictions                                                  |12              |text            |YES        |NULL          |
|public.Domestic Instruments          |Abbreviation                                                   |13              |text            |YES        |NULL          |
|public.Domestic Instruments          |Date                                                           |14              |text            |YES        |NULL          |
|public.Domestic Instruments          |Last Modified                                                  |15              |text            |YES        |NULL          |
|public.Domestic Instruments          |Jurisdictions Alpha-3 Code                                     |16              |text            |YES        |NULL          |
|public.Domestic Instruments          |Created                                                        |17              |text            |YES        |NULL          |
|public.Domestic Instruments          |Last Modified By.id                                            |18              |text            |YES        |NULL          |
|public.Domestic Instruments          |Last Modified By.email                                         |19              |text            |YES        |NULL          |
|public.Domestic Instruments          |Last Modified By.name                                          |20              |text            |YES        |NULL          |
|public.Domestic Instruments          |Created By.id                                                  |21              |text            |YES        |NULL          |
|public.Domestic Instruments          |Created By.email                                               |22              |text            |YES        |NULL          |
|public.Domestic Instruments          |Created By.name                                                |23              |text            |YES        |NULL          |
|public.Domestic Instruments          |Official Title                                                 |24              |text            |YES        |NULL          |
|public.Domestic Instruments          |Full Text of the Provisions                                    |25              |text            |YES        |NULL          |
|public.Domestic Instruments          |Domestic Legal Provisions Link                                 |26              |text            |YES        |NULL          |
|public.Domestic Instruments          |Domestic Legal Provisions Full Text of the Provision (English T|27              |text            |YES        |NULL          |
|public.Domestic Instruments          |Domestic Legal Provisions Full Text of the Provision (Original |28              |text            |YES        |NULL          |
|public.Domestic Instruments          |Domestic Legal Provisions                                      |29              |text            |YES        |NULL          |
|public.Domestic Instruments          |Publication Date                                               |30              |text            |YES        |NULL          |
|public.Domestic Instruments          |Compatible With the UNCITRAL Model Law?                        |31              |boolean         |YES        |NULL          |
|public.Domestic Instruments          |Questions Link                                                 |32              |text            |YES        |NULL          |
|public.Domestic Instruments          |Entry Into Force                                               |33              |text            |YES        |NULL          |
|public.Domestic Instruments          |Compatible With the HCCH Principles?                           |34              |boolean         |YES        |NULL          |
|public.Domestic Instruments          |Replaced by Link                                               |35              |text            |YES        |NULL          |
|public.Domestic Instruments          |Replaced by                                                    |36              |text            |YES        |NULL          |
|public.Domestic Instruments          |Amended by Link                                                |37              |text            |YES        |NULL          |
|public.Domestic Instruments          |Amended by                                                     |38              |text            |YES        |NULL          |
|public.Domestic Instruments          |Amends Link                                                    |39              |text            |YES        |NULL          |
|public.Domestic Instruments          |Amends                                                         |40              |text            |YES        |NULL          |
|public.Domestic Instruments          |search                                                         |41              |tsvector        |YES        |NULL          |
|public.Domestic Instruments          |sort_date                                                      |42              |date            |YES        |NULL          |
|public.Domestic Legal Provisions     |Name                                                           |1               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Article                                                        |2               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Full Text of the Provision (Original Language)                 |3               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Full Text of the Provision (English Translation)               |4               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Domestic Instruments Link                                      |5               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Answers                                                        |6               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Questions                                                      |7               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Record ID                                                      |8               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Legislation Title                                              |9               |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Full Descriptor                                                |10              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Last Modified                                                  |11              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Created                                                        |12              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Last Modified By.id                                            |13              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Last Modified By.email                                         |14              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Last Modified By.name                                          |15              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Created By.id                                                  |16              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Created By.email                                               |17              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Created By.name                                                |18              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Themes Link                                                    |19              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Jurisdictions Link                                             |20              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Jurisdictions                                                  |21              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Court Decisions                                                |22              |text            |YES        |NULL          |
|public.Domestic Legal Provisions     |Answers 2                                                      |23              |text            |YES        |NULL          |
|public.Glossary                      |Keywords                                                       |1               |text            |YES        |NULL          |
|public.Glossary                      |Definition                                                     |2               |text            |YES        |NULL          |
|public.Glossary                      |Source                                                         |3               |text            |YES        |NULL          |
|public.Glossary                      |Time Stamp                                                     |4               |text            |YES        |NULL          |
|public.Glossary                      |Questions Link                                                 |5               |text            |YES        |NULL          |
|public.Glossary                      |Questions                                                      |6               |text            |YES        |NULL          |
|public.Glossary                      |ID-Number                                                      |7               |bigint          |YES        |NULL          |
|public.Glossary                      |Record ID                                                      |8               |text            |YES        |NULL          |
|public.Glossary                      |Relevant for Case Analysis                                     |9               |boolean         |YES        |NULL          |
|public.Glossary                      |Last Modified                                                  |10              |text            |YES        |NULL          |
|public.Glossary                      |Created                                                        |11              |text            |YES        |NULL          |
|public.Glossary                      |Last Modified By.id                                            |12              |text            |YES        |NULL          |
|public.Glossary                      |Last Modified By.email                                         |13              |text            |YES        |NULL          |
|public.Glossary                      |Last Modified By.name                                          |14              |text            |YES        |NULL          |
|public.Glossary                      |Created By.id                                                  |15              |text            |YES        |NULL          |
|public.Glossary                      |Created By.email                                               |16              |text            |YES        |NULL          |
|public.Glossary                      |Created By.name                                                |17              |text            |YES        |NULL          |
|public.HCCH Answers                  |Adapted Question                                               |1               |text            |YES        |NULL          |
|public.HCCH Answers                  |Position                                                       |2               |text            |YES        |NULL          |
|public.HCCH Answers                  |Questions Link                                                 |3               |text            |YES        |NULL          |
|public.HCCH Answers                  |Theme Code (from Original Question)                            |4               |text            |YES        |NULL          |
|public.HCCH Answers                  |Questions Primary Theme                                        |5               |text            |YES        |NULL          |
|public.HCCH Answers                  |Questions ID                                                   |6               |text            |YES        |NULL          |
|public.HCCH Answers                  |International Legal Provisions Title of the Provision          |7               |text            |YES        |NULL          |
|public.HCCH Answers                  |International Legal Provisions Full Text                       |8               |text            |YES        |NULL          |
|public.HCCH Answers                  |International Legal Provisions Link                            |9               |text            |YES        |NULL          |
|public.HCCH Answers                  |International Instruments Link                                 |10              |text            |YES        |NULL          |
|public.HCCH Answers                  |International Instruments                                      |11              |text            |YES        |NULL          |
|public.HCCH Answers                  |ID                                                             |12              |bigint          |YES        |NULL          |
|public.HCCH Answers                  |Last Modified                                                  |13              |text            |YES        |NULL          |
|public.HCCH Answers                  |Themes Link                                                    |14              |text            |YES        |NULL          |
|public.HCCH Answers                  |Themes                                                         |15              |text            |YES        |NULL          |
|public.HCCH Answers                  |Created                                                        |16              |text            |YES        |NULL          |
|public.HCCH Answers                  |Last Modified By.id                                            |17              |text            |YES        |NULL          |
|public.HCCH Answers                  |Last Modified By.email                                         |18              |text            |YES        |NULL          |
|public.HCCH Answers                  |Last Modified By.name                                          |19              |text            |YES        |NULL          |
|public.HCCH Answers                  |Created By.id                                                  |20              |text            |YES        |NULL          |
|public.HCCH Answers                  |Created By.email                                               |21              |text            |YES        |NULL          |
|public.HCCH Answers                  |Created By.name                                                |22              |text            |YES        |NULL          |
|public.HCCH Answers                  |search                                                         |23              |tsvector        |YES        |NULL          |
|public.HCCH Answers                  |sort_date                                                      |24              |date            |YES        |NULL          |
|public.International Instruments     |Name                                                           |1               |text            |YES        |NULL          |
|public.International Instruments     |International Legal Provisions Link                            |2               |text            |YES        |NULL          |
|public.International Instruments     |Specialists Link                                               |3               |text            |YES        |NULL          |
|public.International Instruments     |URL                                                            |4               |text            |YES        |NULL          |
|public.International Instruments     |Attachment                                                     |5               |text            |YES        |NULL          |
|public.International Instruments     |Date                                                           |6               |text            |YES        |NULL          |
|public.International Instruments     |Literature Link                                                |7               |text            |YES        |NULL          |
|public.International Instruments     |HCCH Comparison Link                                           |8               |text            |YES        |NULL          |
|public.International Instruments     |ID Number                                                      |9               |bigint          |YES        |NULL          |
|public.International Instruments     |ID                                                             |10              |text            |YES        |NULL          |
|public.International Instruments     |Last Modified                                                  |11              |text            |YES        |NULL          |
|public.International Instruments     |Specialists                                                    |12              |text            |YES        |NULL          |
|public.International Instruments     |Literature                                                     |13              |text            |YES        |NULL          |
|public.International Instruments     |Created                                                        |14              |text            |YES        |NULL          |
|public.International Instruments     |Last Modified By.id                                            |15              |text            |YES        |NULL          |
|public.International Instruments     |Last Modified By.email                                         |16              |text            |YES        |NULL          |
|public.International Instruments     |Last Modified By.name                                          |17              |text            |YES        |NULL          |
|public.International Instruments     |Created By.id                                                  |18              |text            |YES        |NULL          |
|public.International Instruments     |Created By.email                                               |19              |text            |YES        |NULL          |
|public.International Instruments     |Created By.name                                                |20              |text            |YES        |NULL          |
|public.International Instruments     |search                                                         |21              |tsvector        |YES        |NULL          |
|public.International Instruments     |sort_date                                                      |22              |date            |YES        |NULL          |
|public.International Legal Provisions|Title of the Provision                                         |1               |text            |YES        |NULL          |
|public.International Legal Provisions|Full Text                                                      |2               |text            |YES        |NULL          |
|public.International Legal Provisions|Provision                                                      |3               |text            |YES        |NULL          |
|public.International Legal Provisions|Questions                                                      |4               |text            |YES        |NULL          |
|public.International Legal Provisions|Interface Order                                                |5               |bigint          |YES        |NULL          |
|public.International Legal Provisions|Record ID                                                      |6               |text            |YES        |NULL          |
|public.International Legal Provisions|Instrument Link                                                |7               |text            |YES        |NULL          |
|public.International Legal Provisions|Instrument                                                     |8               |text            |YES        |NULL          |
|public.International Legal Provisions|HCCH Comparison Link                                           |9               |text            |YES        |NULL          |
|public.International Legal Provisions|HCCH Comparison                                                |10              |text            |YES        |NULL          |
|public.International Legal Provisions|ID                                                             |11              |text            |YES        |NULL          |
|public.International Legal Provisions|Literature                                                     |12              |text            |YES        |NULL          |
|public.International Legal Provisions|Last Modified                                                  |13              |text            |YES        |NULL          |
|public.International Legal Provisions|Topic                                                          |14              |text            |YES        |NULL          |
|public.International Legal Provisions|Created                                                        |15              |text            |YES        |NULL          |
|public.International Legal Provisions|Last Modified By.id                                            |16              |text            |YES        |NULL          |
|public.International Legal Provisions|Last Modified By.email                                         |17              |text            |YES        |NULL          |
|public.International Legal Provisions|Last Modified By.name                                          |18              |text            |YES        |NULL          |
|public.International Legal Provisions|Created By.id                                                  |19              |text            |YES        |NULL          |
|public.International Legal Provisions|Created By.email                                               |20              |text            |YES        |NULL          |
|public.International Legal Provisions|Created By.name                                                |21              |text            |YES        |NULL          |
|public.International Legal Provisions|Literature Link                                                |22              |text            |YES        |NULL          |
|public.International Legal Provisions|Arbitral Awards                                                |23              |text            |YES        |NULL          |
|public.Jurisdictions                 |Name                                                           |1               |text            |YES        |NULL          |
|public.Jurisdictions                 |Alpha-3 Code                                                   |2               |text            |YES        |NULL          |
|public.Jurisdictions                 |Type                                                           |3               |text            |YES        |NULL          |
|public.Jurisdictions                 |Court Decisions Link                                           |4               |text            |YES        |NULL          |
|public.Jurisdictions                 |Domestic Instruments Link                                      |5               |text            |YES        |NULL          |
|public.Jurisdictions                 |Answers Link                                                   |6               |text            |YES        |NULL          |
|public.Jurisdictions                 |Region                                                         |7               |text            |YES        |NULL          |
|public.Jurisdictions                 |North/South Divide                                             |8               |text            |YES        |NULL          |
|public.Jurisdictions                 |Record ID                                                      |9               |text            |YES        |NULL          |
|public.Jurisdictions                 |Domestic Legal Provisions Link                                 |10              |text            |YES        |NULL          |
|public.Jurisdictions                 |Literature Link                                                |11              |text            |YES        |NULL          |
|public.Jurisdictions                 |Legal Family                                                   |12              |text            |YES        |NULL          |
|public.Jurisdictions                 |Literature                                                     |13              |text            |YES        |NULL          |
|public.Jurisdictions                 |Specialists Link                                               |14              |text            |YES        |NULL          |
|public.Jurisdictions                 |Last Modified                                                  |15              |text            |YES        |NULL          |
|public.Jurisdictions                 |Literature Title                                               |16              |text            |YES        |NULL          |
|public.Jurisdictions                 |Jurisdiction Summary                                           |17              |text            |YES        |NULL          |
|public.Jurisdictions                 |Created                                                        |18              |text            |YES        |NULL          |
|public.Jurisdictions                 |Jurisdiction Summary New                                       |19              |text            |YES        |NULL          |
|public.Jurisdictions                 |Last Modified By.id                                            |20              |text            |YES        |NULL          |
|public.Jurisdictions                 |Last Modified By.email                                         |21              |text            |YES        |NULL          |
|public.Jurisdictions                 |Last Modified By.name                                          |22              |text            |YES        |NULL          |
|public.Jurisdictions                 |Created By.id                                                  |23              |text            |YES        |NULL          |
|public.Jurisdictions                 |Created By.email                                               |24              |text            |YES        |NULL          |
|public.Jurisdictions                 |Created By.name                                                |25              |text            |YES        |NULL          |
|public.Jurisdictions                 |Irrelevant?                                                    |26              |boolean         |YES        |NULL          |
|public.Jurisdictions                 |Arbitral Institutions Link                                     |27              |text            |YES        |NULL          |
|public.Jurisdictions                 |Done                                                           |28              |boolean         |YES        |NULL          |
|public.Jurisdictions                 |Arbitral Awards Link                                           |29              |text            |YES        |NULL          |
|public.Jurisdictions                 |Jurisdictional Differentiator                                  |30              |text            |YES        |NULL          |
|public.Literature                    |Key                                                            |1               |text            |YES        |NULL          |
|public.Literature                    |Item Type                                                      |2               |text            |YES        |NULL          |
|public.Literature                    |Publication Year                                               |3               |double precision|YES        |NULL          |
|public.Literature                    |Author                                                         |4               |text            |YES        |NULL          |
|public.Literature                    |Title                                                          |5               |text            |YES        |NULL          |
|public.Literature                    |ISBN                                                           |6               |text            |YES        |NULL          |
|public.Literature                    |ISSN                                                           |7               |text            |YES        |NULL          |
|public.Literature                    |Url                                                            |8               |text            |YES        |NULL          |
|public.Literature                    |Date                                                           |9               |text            |YES        |NULL          |
|public.Literature                    |Date Added                                                     |10              |text            |YES        |NULL          |
|public.Literature                    |Date Modified                                                  |11              |text            |YES        |NULL          |
|public.Literature                    |Publisher                                                      |12              |text            |YES        |NULL          |
|public.Literature                    |Language                                                       |13              |text            |YES        |NULL          |
|public.Literature                    |Extra                                                          |14              |text            |YES        |NULL          |
|public.Literature                    |Manual Tags                                                    |15              |text            |YES        |NULL          |
|public.Literature                    |Editor                                                         |16              |text            |YES        |NULL          |
|public.Literature                    |ID                                                             |17              |bigint          |YES        |NULL          |
|public.Literature                    |Jurisdiction                                                   |18              |text            |YES        |NULL          |
|public.Literature                    |International Instruments Link                                 |19              |text            |YES        |NULL          |
|public.Literature                    |International Instruments                                      |20              |text            |YES        |NULL          |
|public.Literature                    |Last Modified                                                  |21              |text            |YES        |NULL          |
|public.Literature                    |Created                                                        |22              |text            |YES        |NULL          |
|public.Literature                    |Last Modified By.id                                            |23              |text            |YES        |NULL          |
|public.Literature                    |Last Modified By.email                                         |24              |text            |YES        |NULL          |
|public.Literature                    |Last Modified By.name                                          |25              |text            |YES        |NULL          |
|public.Literature                    |Created By.id                                                  |26              |text            |YES        |NULL          |
|public.Literature                    |Created By.email                                               |27              |text            |YES        |NULL          |
|public.Literature                    |Created By.name                                                |28              |text            |YES        |NULL          |
|public.Literature                    |Publication Title                                              |29              |text            |YES        |NULL          |
|public.Literature                    |Issue                                                          |30              |double precision|YES        |NULL          |
|public.Literature                    |Volume                                                         |31              |double precision|YES        |NULL          |
|public.Literature                    |International Legal Provisions Link                            |32              |text            |YES        |NULL          |
|public.Literature                    |International Legal Provisions                                 |33              |text            |YES        |NULL          |
|public.Literature                    |Themes Link                                                    |34              |text            |YES        |NULL          |
|public.Literature                    |Themes                                                         |35              |text            |YES        |NULL          |
|public.Literature                    |Pages                                                          |36              |text            |YES        |NULL          |
|public.Literature                    |Jurisdiction Link                                              |37              |text            |YES        |NULL          |
|public.Literature                    |Abstract Note                                                  |38              |text            |YES        |NULL          |
|public.Literature                    |Library Catalog                                                |39              |text            |YES        |NULL          |
|public.Literature                    |DOI                                                            |40              |text            |YES        |NULL          |
|public.Literature                    |Access Date                                                    |41              |text            |YES        |NULL          |
|public.Literature                    |Open Access                                                    |42              |boolean         |YES        |NULL          |
|public.Literature                    |Open Access URL                                                |43              |text            |YES        |NULL          |
|public.Literature                    |Journal Abbreviation                                           |44              |text            |YES        |NULL          |
|public.Literature                    |Short Title                                                    |45              |text            |YES        |NULL          |
|public.Literature                    |Place                                                          |46              |text            |YES        |NULL          |
|public.Literature                    |Num Pages                                                      |47              |double precision|YES        |NULL          |
|public.Literature                    |Type                                                           |48              |text            |YES        |NULL          |
|public.Literature                    |OUP JD Chapter                                                 |49              |boolean         |YES        |NULL          |
|public.Literature                    |Jurisdiction Summary                                           |50              |text            |YES        |NULL          |
|public.Literature                    |Contributor                                                    |51              |text            |YES        |NULL          |
|public.Literature                    |Automatic Tags                                                 |52              |text            |YES        |NULL          |
|public.Literature                    |Number                                                         |53              |double precision|YES        |NULL          |
|public.Literature                    |Series                                                         |54              |text            |YES        |NULL          |
|public.Literature                    |Series Number                                                  |55              |double precision|YES        |NULL          |
|public.Literature                    |Regional Instruments Link                                      |56              |text            |YES        |NULL          |
|public.Literature                    |Answers                                                        |57              |text            |YES        |NULL          |
|public.Literature                    |Series Editor                                                  |58              |text            |YES        |NULL          |
|public.Literature                    |Edition                                                        |59              |text            |YES        |NULL          |
|public.Literature                    |Call Number                                                    |60              |text            |YES        |NULL          |
|public.Literature                    |search                                                         |61              |tsvector        |YES        |NULL          |
|public.Literature                    |sort_date                                                      |62              |date            |YES        |NULL          |
|public.Questions                     |ID                                                             |1               |text            |YES        |NULL          |
|public.Questions                     |Theme Code                                                     |2               |text            |YES        |NULL          |
|public.Questions                     |Question                                                       |3               |text            |YES        |NULL          |
|public.Questions                     |Answers                                                        |4               |text            |YES        |NULL          |
|public.Questions                     |Jurisdiction (from Answers)                                    |5               |text            |YES        |NULL          |
|public.Questions                     |Concepts                                                       |6               |text            |YES        |NULL          |
|public.Questions                     |Record ID                                                      |7               |text            |YES        |NULL          |
|public.Questions                     |Question Number                                                |8               |text            |YES        |NULL          |
|public.Questions                     |Primary Theme                                                  |9               |text            |YES        |NULL          |
|public.Questions                     |Answering Options                                              |10              |text            |YES        |NULL          |
|public.Questions                     |International Legal Provisions Link                            |11              |text            |YES        |NULL          |
|public.Questions                     |Questionnaire Version                                          |12              |text            |YES        |NULL          |
|public.Questions                     |Last Modified                                                  |13              |text            |YES        |NULL          |
|public.Questions                     |Themes Link                                                    |14              |text            |YES        |NULL          |
|public.Questions                     |Created                                                        |15              |text            |YES        |NULL          |
|public.Questions                     |Last Modified By.id                                            |16              |text            |YES        |NULL          |
|public.Questions                     |Last Modified By.email                                         |17              |text            |YES        |NULL          |
|public.Questions                     |Last Modified By.name                                          |18              |text            |YES        |NULL          |
|public.Questions                     |Created By.id                                                  |19              |text            |YES        |NULL          |
|public.Questions                     |Created By.email                                               |20              |text            |YES        |NULL          |
|public.Questions                     |Created By.name                                                |21              |text            |YES        |NULL          |
|public.Questions                     |Court Decisions Link                                           |22              |text            |YES        |NULL          |
|public.Questions                     |International Legal Provisions copy                            |23              |text            |YES        |NULL          |
|public.Questions                     |Domestic Legal Provisions Link                                 |24              |text            |YES        |NULL          |
|public.Questions                     |Filtering Index                                                |25              |double precision|YES        |NULL          |
|public.Questions                     |HCCH Comparison Link                                           |26              |text            |YES        |NULL          |
|public.Questions                     |Domestic Instruments Link                                      |27              |text            |YES        |NULL          |
|public.Questions                     |Question in Accessible Language                                |28              |text            |YES        |NULL          |
|public.Regional Instruments          |ID                                                             |1               |text            |YES        |NULL          |
|public.Regional Instruments          |Abbreviation                                                   |2               |text            |YES        |NULL          |
|public.Regional Instruments          |Specialists Link                                               |3               |text            |YES        |NULL          |
|public.Regional Instruments          |ID Number                                                      |4               |bigint          |YES        |NULL          |
|public.Regional Instruments          |Last Modified                                                  |5               |text            |YES        |NULL          |
|public.Regional Instruments          |Specialists                                                    |6               |text            |YES        |NULL          |
|public.Regional Instruments          |Literature                                                     |7               |text            |YES        |NULL          |
|public.Regional Instruments          |Regional Legal Provisions Link                                 |8               |text            |YES        |NULL          |
|public.Regional Instruments          |Created                                                        |9               |text            |YES        |NULL          |
|public.Regional Instruments          |Title                                                          |10              |text            |YES        |NULL          |
|public.Regional Instruments          |Regional Legal Provisions                                      |11              |text            |YES        |NULL          |
|public.Regional Instruments          |Last Modified By.id                                            |12              |text            |YES        |NULL          |
|public.Regional Instruments          |Last Modified By.email                                         |13              |text            |YES        |NULL          |
|public.Regional Instruments          |Last Modified By.name                                          |14              |text            |YES        |NULL          |
|public.Regional Instruments          |Created By.id                                                  |15              |text            |YES        |NULL          |
|public.Regional Instruments          |Created By.email                                               |16              |text            |YES        |NULL          |
|public.Regional Instruments          |Created By.name                                                |17              |text            |YES        |NULL          |
|public.Regional Instruments          |Attachment                                                     |18              |text            |YES        |NULL          |
|public.Regional Instruments          |Date                                                           |19              |text            |YES        |NULL          |
|public.Regional Instruments          |Literature Link                                                |20              |text            |YES        |NULL          |
|public.Regional Instruments          |URL                                                            |21              |text            |YES        |NULL          |
|public.Regional Instruments          |search                                                         |22              |tsvector        |YES        |NULL          |
|public.Regional Instruments          |sort_date                                                      |23              |date            |YES        |NULL          |
|public.Regional Legal Provisions     |ID                                                             |1               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Title of the Provision                                         |2               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Full Text                                                      |3               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Provision                                                      |4               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Record ID                                                      |5               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Instrument Link                                                |6               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Instrument                                                     |7               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |HCCH Comparison                                                |8               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Literature                                                     |9               |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Last Modified                                                  |10              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Topic                                                          |11              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Created                                                        |12              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Last Modified By.id                                            |13              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Last Modified By.email                                         |14              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Last Modified By.name                                          |15              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Created By.id                                                  |16              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Created By.email                                               |17              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Created By.name                                                |18              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Questions                                                      |19              |text            |YES        |NULL          |
|public.Regional Legal Provisions     |Interface Order                                                |20              |double precision|YES        |NULL          |
|public.Specialists                   |Specialist                                                     |1               |text            |YES        |NULL          |
|public.Specialists                   |Last Modified                                                  |2               |text            |YES        |NULL          |
|public.Specialists                   |Regional Instruments Link                                      |3               |text            |YES        |NULL          |
|public.Specialists                   |Created                                                        |4               |text            |YES        |NULL          |
|public.Specialists                   |Regional Instruments                                           |5               |text            |YES        |NULL          |
|public.Specialists                   |Last Modified By.id                                            |6               |text            |YES        |NULL          |
|public.Specialists                   |Last Modified By.email                                         |7               |text            |YES        |NULL          |
|public.Specialists                   |Last Modified By.name                                          |8               |text            |YES        |NULL          |
|public.Specialists                   |Created By.id                                                  |9               |text            |YES        |NULL          |
|public.Specialists                   |Created By.email                                               |10              |text            |YES        |NULL          |
|public.Specialists                   |Created By.name                                                |11              |text            |YES        |NULL          |
|public.Specialists                   |Jurisdiction Link                                              |12              |text            |YES        |NULL          |
|public.Specialists                   |Jurisdiction                                                   |13              |text            |YES        |NULL          |
|public.Specialists                   |International Instruments Link                                 |14              |text            |YES        |NULL          |
|public.Specialists                   |International Instruments                                      |15              |text            |YES        |NULL          |
|public.Themes                        |Theme                                                          |1               |text            |YES        |NULL          |
|public.Themes                        |Questions                                                      |2               |text            |YES        |NULL          |
|public.Themes                        |Domestic Legal Provisions                                      |3               |text            |YES        |NULL          |
|public.Themes                        |Last Modified                                                  |4               |text            |YES        |NULL          |
|public.Themes                        |Created                                                        |5               |text            |YES        |NULL          |
|public.Themes                        |Topics                                                         |6               |text            |YES        |NULL          |
|public.Themes                        |Last Modified By.id                                            |7               |text            |YES        |NULL          |
|public.Themes                        |Last Modified By.email                                         |8               |text            |YES        |NULL          |
|public.Themes                        |Last Modified By.name                                          |9               |text            |YES        |NULL          |
|public.Themes                        |Created By.id                                                  |10              |text            |YES        |NULL          |
|public.Themes                        |Created By.email                                               |11              |text            |YES        |NULL          |
|public.Themes                        |Created By.name                                                |12              |text            |YES        |NULL          |
|public.Themes                        |HCCH Comparison                                                |13              |text            |YES        |NULL          |
|public.Themes                        |Literature                                                     |14              |text            |YES        |NULL          |
|public.Themes                        |Arbitral Awards                                                |15              |text            |YES        |NULL          |
|public.Topics                        |Topic                                                          |1               |text            |YES        |NULL          |
|public.Topics                        |Regional Legal Provisions Link                                 |2               |text            |YES        |NULL          |
|public.Topics                        |International Legal Provisions Link                            |3               |text            |YES        |NULL          |
|public.Topics                        |Last Modified                                                  |4               |text            |YES        |NULL          |
|public.Topics                        |Created                                                        |5               |text            |YES        |NULL          |
|public.Topics                        |Themes                                                         |6               |text            |YES        |NULL          |
|public.Topics                        |Theme (from Themes)                                            |7               |text            |YES        |NULL          |
|public.Topics                        |Last Modified By.id                                            |8               |text            |YES        |NULL          |
|public.Topics                        |Last Modified By.email                                         |9               |text            |YES        |NULL          |
|public.Topics                        |Last Modified By.name                                          |10              |text            |YES        |NULL          |
|public.Topics                        |Created By.id                                                  |11              |text            |YES        |NULL          |
|public.Topics                        |Created By.email                                               |12              |text            |YES        |NULL          |
|public.Topics                        |Created By.name                                                |13              |text            |YES        |NULL          |




Schema of the new Postgres database used in NocoDB (with the actually interesting data laying in the "p1q5x3pj29vkrdr" schema):

|table_full_name                                         |column_name                                     |ordinal_position|data_type                  |is_nullable|column_default                                                              |
|--------------------------------------------------------|------------------------------------------------|----------------|---------------------------|-----------|----------------------------------------------------------------------------|
|p1q5x3pj29vkrdr.Abbreviations                           |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Abbreviations_id_seq"'::regclass)                 |
|p1q5x3pj29vkrdr.Abbreviations                           |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Abbreviation                                    |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Designation                                     |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Type                                            |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Abbreviations                           |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Answers_id_seq"'::regclass)                       |
|p1q5x3pj29vkrdr.Answers                                 |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |Answer                                          |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |Interesting_Answer                              |10              |smallint                   |YES        |0                                                                           |
|p1q5x3pj29vkrdr.Answers                                 |More_Information                                |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |To_Review_                                      |12              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Answers                                 |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |OUP_Book_Quote                                  |14              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |Last_Modified                                   |15              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |Last_Modified_By                                |16              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Answers                                 |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Arbitral_Awards_id_seq"'::regclass)               |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Case_Number                                     |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Context                                         |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Award_Summary                                   |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Year                                            |12              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Nature_of_the_Award                             |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Seat__Town_                                     |14              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Source                                          |15              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Last_Modified                                   |16              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Last_Modified_By                                |17              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |ID_Number                                       |18              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Created_By                                      |19              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Awards                         |Created                                         |20              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Arbitral_Institutions_id_seq"'::regclass)         |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |Institution                                     |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |Abbreviation                                    |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |Last_Modified                                   |11              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |Last_Modified_By                                |12              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |Created_By                                      |13              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Institutions                   |Created                                         |14              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Arbitral_Rules_id_seq"'::regclass)                |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |Set_of_Rules                                    |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |In_Force_From                                   |10              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |Official_Source__URL_                           |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Arbitral_Rules                          |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Court_Decisions_id_seq"'::regclass)               |
|p1q5x3pj29vkrdr.Court_Decisions                         |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Case_Citation                                   |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Official_Source__URL_                           |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Official_Source__PDF_                           |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Abstract                                        |12              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Internal_Notes                                  |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |English_Translation                             |14              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |PIL_Provisions                                  |15              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Choice_of_Law_Issue                             |16              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Court_s_Position                                |17              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Text_of_the_Relevant_Legal_Provisions           |18              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Translated_Excerpt                              |19              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Quote                                           |20              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Copyright_Issues                                |21              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Court_Decisions                         |Relevant_Facts                                  |22              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |ID_number                                       |23              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Case_Rank                                       |24              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Date_of_Judgment                                |25              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Original_Text                                   |26              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Created                                         |27              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Last_Modified_By                                |28              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Added_By                                        |29              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Date                                            |30              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Case_Title                                      |31              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Instance                                        |32              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Official_Keywords                               |33              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Last_Modified                                   |34              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Publication_Date_ISO                            |35              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Created_By                                      |36              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Court_Decisions                         |Created_time                                    |37              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Domestic_Instruments_id_seq"'::regclass)          |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Title__in_English_                              |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Relevant_Provisions                             |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Full_Text_of_the_Provisions                     |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Official_Title                                  |12              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Publication_Date                                |13              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Entry_Into_Force                                |14              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Source__URL_                                    |15              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Source__PDF_                                    |16              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |ID_number                                       |17              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Compatible_With_the_HCCH_Principles_            |18              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Abbreviation                                    |19              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Compatible_With_the_UNCITRAL_Model_Law_         |20              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Date                                            |21              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Last_Modified                                   |22              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Last_Modified_By                                |23              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Created_By                                      |24              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Instruments                    |Created                                         |25              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Domestic_Legal_Provisions_id_seq"'::regclass)     |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Article                                         |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Full_Text_of_the_Provision__Original_Language_  |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Full_Text_of_the_Provision__English_Translation_|11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Domestic_Legal_Provisions               |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Glossary_id_seq"'::regclass)                      |
|p1q5x3pj29vkrdr.Glossary                                |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Keywords                                        |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Definition                                      |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Source                                          |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Time_Stamp                                      |12              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |ID_Number                                       |13              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Relevant_for_Case_Analysis                      |14              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Glossary                                |Last_Modified                                   |15              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Last_Modified_By                                |16              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Glossary                                |Created                                         |18              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."HCCH_Answers_id_seq"'::regclass)                  |
|p1q5x3pj29vkrdr.HCCH_Answers                            |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |Adapted_Question                                |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |Position                                        |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |ID_1                                            |11              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.HCCH_Answers                            |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."International_Instruments_id_seq"'::regclass)     |
|p1q5x3pj29vkrdr.International_Instruments               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Name                                            |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |URL                                             |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Attachment                                      |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Date                                            |12              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |ID_Number                                       |13              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |International_Legal_Provisions_copy             |16              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Instruments               |Created                                         |18              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."International_Legal_Provisions_id_seq"'::regclass)|
|p1q5x3pj29vkrdr.International_Legal_Provisions          |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Title_of_the_Provision                          |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Full_Text                                       |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Provision                                       |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Interface_Order                                 |12              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Arbitral_Awards                                 |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |International_Instruments_copy                  |16              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.International_Legal_Provisions          |Created                                         |18              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Jurisdictions_id_seq"'::regclass)                 |
|p1q5x3pj29vkrdr.Jurisdictions                           |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Name                                            |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Alpha_3_Code                                    |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Type                                            |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Region                                          |12              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |North_South_Divide                              |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Irrelevant_                                     |14              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Jurisdictions                           |Jurisdictional_Differentiator                   |15              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Done                                            |16              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Jurisdictions                           |Legal_Family                                    |17              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Last_Modified                                   |18              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Last_Modified_By                                |19              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Created_By                                      |21              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Created                                         |22              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Jurisdictions                           |Jurisdiction_Summary                            |23              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Literature_id_seq"'::regclass)                    |
|p1q5x3pj29vkrdr.Literature                              |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Item_Type                                       |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Publication_Year                                |11              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Author                                          |12              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Title                                           |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Publication_Title                               |14              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |ISBN                                            |15              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |ISSN                                            |16              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |DOI                                             |17              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Url                                             |18              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Abstract_Note                                   |19              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Date                                            |20              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Date_Added                                      |21              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Date_Modified                                   |22              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Access_Date                                     |23              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Pages                                           |24              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Num_Pages                                       |25              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Issue                                           |26              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Volume                                          |27              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Journal_Abbreviation                            |29              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Short_Title                                     |30              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Series                                          |31              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Series_Number                                   |32              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Publisher                                       |35              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Place                                           |36              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Language                                        |37              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Type                                            |39              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Library_Catalog                                 |42              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Call_Number                                     |43              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Extra                                           |44              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Manual_Tags                                     |47              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Automatic_Tags                                  |48              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Editor                                          |49              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Series_Editor                                   |50              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Contributor                                     |52              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Number                                          |67              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Edition                                         |68              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |ID_1                                            |95              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |OUP_JD_Chapter                                  |96              |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Literature                              |Last_Modified                                   |97              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Jurisdiction_Summary                            |98              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Last_Modified_By                                |99              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Created_By                                      |100             |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Created                                         |101             |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Literature                              |Open_Access                                     |102             |boolean                    |YES        |false                                                                       |
|p1q5x3pj29vkrdr.Literature                              |Open_Access_URL                                 |103             |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Questions_id_seq"'::regclass)                     |
|p1q5x3pj29vkrdr.Questions                               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Theme_Code                                      |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Question                                        |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Question_Number                                 |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Primary_Theme                                   |12              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Answering_Options                               |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Question_in_Accessible_Language                 |14              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Questionnaire_Version                           |15              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Last_Modified                                   |16              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Last_Modified_By                                |17              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Filtering_Index                                 |18              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Created_By                                      |19              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Questions                               |Created                                         |20              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Regional_Instruments_id_seq"'::regclass)          |
|p1q5x3pj29vkrdr.Regional_Instruments                    |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Abbreviation                                    |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |URL                                             |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Attachment                                      |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Date                                            |12              |date                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |ID_Number                                       |13              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Created_By                                      |16              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Created                                         |17              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Instruments                    |Title                                           |18              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Regional_Legal_Provisions_id_seq"'::regclass)     |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Title_of_the_Provision                          |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Full_Text                                       |10              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Provision                                       |11              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Interface_Order                                 |12              |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Arbitral_Awards                                 |13              |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Created_By                                      |16              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Regional_Legal_Provisions               |Created                                         |17              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Specialists_id_seq"'::regclass)                   |
|p1q5x3pj29vkrdr.Specialists                             |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |Specialist                                      |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |Last_Modified                                   |10              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |Last_Modified_By                                |11              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |Created_By                                      |12              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Specialists                             |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Themes_id_seq"'::regclass)                        |
|p1q5x3pj29vkrdr.Themes                                  |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |Theme                                           |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |Last_Modified_By                                |10              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |Last_Modified                                   |11              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |Created_By                                      |12              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Themes                                  |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |id                                              |1               |integer                    |NO         |nextval('p1q5x3pj29vkrdr."Topics_id_seq"'::regclass)                        |
|p1q5x3pj29vkrdr.Topics                                  |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |Topic                                           |9               |text                       |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |Last_Modified_By                                |10              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |Last_Modified                                   |11              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |Created_By                                      |12              |character varying          |YES        |NULL                                                                        |
|p1q5x3pj29vkrdr.Topics                                  |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Court_Decisions         |Court_Decisions_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Court_Decisions         |Answers_id                                      |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Domestic_Instru         |Domestic_Instruments_id                         |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Domestic_Instru         |Answers_id                                      |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Domestic_Legal_         |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Domestic_Legal_         |Answers_id                                      |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Domestic_Legal_1        |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Domestic_Legal_1        |Answers_id                                      |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Literature              |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Answers_Literature              |Answers_id                                      |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Arbitral_Instit_Arbitral_Awards |Arbitral_Awards_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Arbitral_Instit_Arbitral_Awards |Arbitral_Institutions_id                        |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Arbitral_Instit_Arbitral_Rules  |Arbitral_Rules_id                               |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Arbitral_Instit_Arbitral_Rules  |Arbitral_Institutions_id                        |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Court_Decisions_Arbitral_Awards |Arbitral_Awards_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Court_Decisions_Arbitral_Awards |Court_Decisions_id                              |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru |Domestic_Instruments1_id                        |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru |Domestic_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru1|Domestic_Instruments1_id                        |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru1|Domestic_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru2|Domestic_Instruments1_id                        |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru2|Domestic_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru3|Domestic_Instruments1_id                        |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Instru3|Domestic_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Legal_ |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Instru_Domestic_Legal_ |Domestic_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Legal__Court_Decisions |Court_Decisions_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Domestic_Legal__Court_Decisions |Domestic_Legal_Provisions_id                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_International_I    |International_Instruments_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_International_I    |HCCH_Answers_id                                 |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_International_L    |International_Legal_Provisions_id               |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_International_L    |HCCH_Answers_id                                 |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_Regional_Instru    |Regional_Instruments_id                         |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_Regional_Instru    |HCCH_Answers_id                                 |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_Regional_Legal_    |Regional_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_HCCH_Answers_Regional_Legal_    |HCCH_Answers_id                                 |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_I_International_L |International_Legal_Provisions_id               |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_I_International_L |International_Instruments_id                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_I_Literature      |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_I_Literature      |International_Instruments_id                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_I_Specialists     |Specialists_id                                  |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_I_Specialists     |International_Instruments_id                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_L_Literature      |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_L_Literature      |International_Legal_Provisions_id               |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_L_Topics          |Topics_id                                       |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_International_L_Topics          |International_Legal_Provisions_id               |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Answers           |Answers_id                                      |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Answers           |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Arbitral_Awards   |Arbitral_Awards_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Arbitral_Awards   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Arbitral_Instit   |Arbitral_Institutions_id                        |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Arbitral_Instit   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Court_Decisions   |Court_Decisions_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Court_Decisions   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Domestic_Instru   |Domestic_Instruments_id                         |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Domestic_Instru   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Domestic_Legal_   |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Domestic_Legal_   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Literature        |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Literature        |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Specialists       |Specialists_id                                  |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Jurisdictions_Specialists       |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Answers               |Answers_id                                      |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Answers               |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Court_Decisions       |Court_Decisions_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Court_Decisions       |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Domestic_Instru       |Domestic_Instruments_id                         |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Domestic_Instru       |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Domestic_Legal_       |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Domestic_Legal_       |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Glossary              |Glossary_id                                     |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Glossary              |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_HCCH_Answers          |HCCH_Answers_id                                 |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_HCCH_Answers          |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_International_L       |International_Legal_Provisions_id               |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_International_L       |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Regional_Legal_       |Regional_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Questions_Regional_Legal_       |Questions_id                                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Instru_Literature      |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Instru_Literature      |Regional_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Instru_Regional_Legal_ |Regional_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Instru_Regional_Legal_ |Regional_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Instru_Specialists     |Specialists_id                                  |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Instru_Specialists     |Regional_Instruments_id                         |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Legal__Literature      |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Legal__Literature      |Regional_Legal_Provisions_id                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Legal__Topics          |Topics_id                                       |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Regional_Legal__Topics          |Regional_Legal_Provisions_id                    |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Arbitral_Awards          |Arbitral_Awards_id                              |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Arbitral_Awards          |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Domestic_Legal_          |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Domestic_Legal_          |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_HCCH_Answers             |HCCH_Answers_id                                 |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_HCCH_Answers             |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Literature               |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Literature               |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Questions                |Questions_id                                    |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Questions                |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Topics                   |Topics_id                                       |1               |integer                    |NO         |NULL                                                                        |
|p1q5x3pj29vkrdr._nc_m2m_Themes_Topics                   |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|p7rc132vhvth1lk.Features                                |id                                              |1               |integer                    |NO         |nextval('p7rc132vhvth1lk."Features_id_seq"'::regclass)                      |
|p7rc132vhvth1lk.Features                                |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|p7rc132vhvth1lk.Features                                |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|p7rc132vhvth1lk.Features                                |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|p7rc132vhvth1lk.Features                                |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|p7rc132vhvth1lk.Features                                |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|p7rc132vhvth1lk.Features                                |title                                           |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Abbreviations_id_seq"'::regclass)                 |
|pejp04izqnshduq.Abbreviations                           |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Abbreviation                                    |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Designation                                     |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Type                                            |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Abbreviations                           |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Answers_id_seq"'::regclass)                       |
|pejp04izqnshduq.Answers                                 |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |Answer                                          |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |Interesting_Answer                              |10              |smallint                   |YES        |0                                                                           |
|pejp04izqnshduq.Answers                                 |More_Information                                |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |To_Review_                                      |12              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Answers                                 |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |OUP_Book_Quote                                  |14              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |Last_Modified                                   |15              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |Last_Modified_By                                |16              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Answers                                 |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Arbitral_Awards_id_seq"'::regclass)               |
|pejp04izqnshduq.Arbitral_Awards                         |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Case_Number                                     |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Context                                         |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Award_Summary                                   |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Year                                            |12              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Nature_of_the_Award                             |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Seat__Town_                                     |14              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Source                                          |15              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Last_Modified                                   |16              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Last_Modified_By                                |17              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |ID_Number                                       |18              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Created_By                                      |19              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Awards                         |Created                                         |20              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Arbitral_Institutions_id_seq"'::regclass)         |
|pejp04izqnshduq.Arbitral_Institutions                   |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |Institution                                     |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |Abbreviation                                    |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |Last_Modified                                   |11              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |Last_Modified_By                                |12              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |Created_By                                      |13              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Institutions                   |Created                                         |14              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Arbitral_Rules_id_seq"'::regclass)                |
|pejp04izqnshduq.Arbitral_Rules                          |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |Set_of_Rules                                    |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |In_Force_From                                   |10              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |Official_Source__URL_                           |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Arbitral_Rules                          |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Court_Decisions_id_seq"'::regclass)               |
|pejp04izqnshduq.Court_Decisions                         |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Case_Citation                                   |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Official_Source__URL_                           |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Official_Source__PDF_                           |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Abstract                                        |12              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Internal_Notes                                  |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |English_Translation                             |14              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |PIL_Provisions                                  |15              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Choice_of_Law_Issue                             |16              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Court_s_Position                                |17              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Text_of_the_Relevant_Legal_Provisions           |18              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Translated_Excerpt                              |19              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Quote                                           |20              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Copyright_Issues                                |21              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Court_Decisions                         |Relevant_Facts                                  |22              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |ID_number                                       |23              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Case_Rank                                       |24              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Date_of_Judgment                                |25              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Original_Text                                   |26              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Created                                         |27              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Last_Modified_By                                |28              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Added_By                                        |29              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Date                                            |30              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Case_Title                                      |31              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Instance                                        |32              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Official_Keywords                               |33              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Last_Modified                                   |34              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Publication_Date_ISO                            |35              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Created_By                                      |36              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Court_Decisions                         |Created_time                                    |37              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Domestic_Instruments_id_seq"'::regclass)          |
|pejp04izqnshduq.Domestic_Instruments                    |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Title__in_English_                              |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Relevant_Provisions                             |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Full_Text_of_the_Provisions                     |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Official_Title                                  |12              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Publication_Date                                |13              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Entry_Into_Force                                |14              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Source__URL_                                    |15              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Source__PDF_                                    |16              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |ID_number                                       |17              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Compatible_With_the_HCCH_Principles_            |18              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Domestic_Instruments                    |Abbreviation                                    |19              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Compatible_With_the_UNCITRAL_Model_Law_         |20              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Domestic_Instruments                    |Date                                            |21              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Last_Modified                                   |22              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Last_Modified_By                                |23              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Created_By                                      |24              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Instruments                    |Created                                         |25              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Domestic_Legal_Provisions_id_seq"'::regclass)     |
|pejp04izqnshduq.Domestic_Legal_Provisions               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Article                                         |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Full_Text_of_the_Provision__Original_Language_  |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Full_Text_of_the_Provision__English_Translation_|11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Domestic_Legal_Provisions               |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Glossary_id_seq"'::regclass)                      |
|pejp04izqnshduq.Glossary                                |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Keywords                                        |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Definition                                      |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Source                                          |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Time_Stamp                                      |12              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |ID_Number                                       |13              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Relevant_for_Case_Analysis                      |14              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Glossary                                |Last_Modified                                   |15              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Last_Modified_By                                |16              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Glossary                                |Created                                         |18              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."HCCH_Answers_id_seq"'::regclass)                  |
|pejp04izqnshduq.HCCH_Answers                            |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |Adapted_Question                                |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |Position                                        |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |ID_1                                            |11              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |Last_Modified                                   |12              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |Last_Modified_By                                |13              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |Created_By                                      |14              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.HCCH_Answers                            |Created                                         |15              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."International_Instruments_id_seq"'::regclass)     |
|pejp04izqnshduq.International_Instruments               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Name                                            |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |URL                                             |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Attachment                                      |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Date                                            |12              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |ID_Number                                       |13              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |International_Legal_Provisions_copy             |16              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Instruments               |Created                                         |18              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."International_Legal_Provisions_id_seq"'::regclass)|
|pejp04izqnshduq.International_Legal_Provisions          |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Title_of_the_Provision                          |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Full_Text                                       |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Provision                                       |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Interface_Order                                 |12              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Arbitral_Awards                                 |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |International_Instruments_copy                  |16              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Created_By                                      |17              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.International_Legal_Provisions          |Created                                         |18              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Jurisdictions_id_seq"'::regclass)                 |
|pejp04izqnshduq.Jurisdictions                           |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Name                                            |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Alpha_3_Code                                    |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Type                                            |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Region                                          |12              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |North_South_Divide                              |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Irrelevant_                                     |14              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Jurisdictions                           |Jurisdictional_Differentiator                   |15              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Done                                            |16              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Jurisdictions                           |Legal_Family                                    |17              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Last_Modified                                   |18              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Last_Modified_By                                |19              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Jurisdiction_Summary                            |20              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Created_By                                      |21              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Created                                         |22              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Jurisdictions                           |Jurisdiction_Summary_New                        |23              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Literature_id_seq"'::regclass)                    |
|pejp04izqnshduq.Literature                              |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Key                                             |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Item_Type                                       |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Publication_Year                                |11              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Author                                          |12              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Title                                           |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Publication_Title                               |14              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |ISBN                                            |15              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |ISSN                                            |16              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |DOI                                             |17              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Url                                             |18              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Abstract_Note                                   |19              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Date                                            |20              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Date_Added                                      |21              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Date_Modified                                   |22              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Access_Date                                     |23              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Pages                                           |24              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Num_Pages                                       |25              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Issue                                           |26              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Volume                                          |27              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Number_Of_Volumes                               |28              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Journal_Abbreviation                            |29              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Short_Title                                     |30              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Series                                          |31              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Series_Number                                   |32              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Series_Text                                     |33              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Series_Title                                    |34              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Publisher                                       |35              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Place                                           |36              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Language                                        |37              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Rights                                          |38              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Type                                            |39              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Archive                                         |40              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Archive_Location                                |41              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Library_Catalog                                 |42              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Call_Number                                     |43              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Extra                                           |44              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Notes                                           |45              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Link_Attachments                                |46              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Manual_Tags                                     |47              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Automatic_Tags                                  |48              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Editor                                          |49              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Series_Editor                                   |50              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Translator                                      |51              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Contributor                                     |52              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Attorney_Agent                                  |53              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Book_Author                                     |54              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Cast_Member                                     |55              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Commenter                                       |56              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Composer                                        |57              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Cosponsor                                       |58              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Counsel                                         |59              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Interviewer                                     |60              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Producer                                        |61              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Recipient                                       |62              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Reviewed_Author                                 |63              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Scriptwriter                                    |64              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Words_By                                        |65              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Guest                                           |66              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Number                                          |67              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Edition                                         |68              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Running_Time                                    |69              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Scale                                           |70              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Medium                                          |71              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Artwork_Size                                    |72              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Filing_Date                                     |73              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Application_Number                              |74              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Assignee                                        |75              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Issuing_Authority                               |76              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Country                                         |77              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Meeting_Name                                    |78              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Conference_Name                                 |79              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Court                                           |80              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |References                                      |81              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Reporter                                        |82              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Legal_Status                                    |83              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Priority_Numbers                                |84              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Programming_Language                            |85              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Version                                         |86              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |System                                          |87              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Code                                            |88              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Code_Number                                     |89              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Section                                         |90              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Session                                         |91              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Committee                                       |92              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |History                                         |93              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Legislative_Body                                |94              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |ID_1                                            |95              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |OUP_JD_Chapter                                  |96              |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Literature                              |Last_Modified                                   |97              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Jurisdiction_Summary                            |98              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Last_Modified_By                                |99              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Created_By                                      |100             |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Created                                         |101             |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Literature                              |Open_Access                                     |102             |boolean                    |YES        |false                                                                       |
|pejp04izqnshduq.Literature                              |Open_Access_URL                                 |103             |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Questions_id_seq"'::regclass)                     |
|pejp04izqnshduq.Questions                               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Theme_Code                                      |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Question                                        |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Question_Number                                 |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Primary_Theme                                   |12              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Answering_Options                               |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Question_in_Accessible_Language                 |14              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Questionnaire_Version                           |15              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Last_Modified                                   |16              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Last_Modified_By                                |17              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Filtering_Index                                 |18              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Created_By                                      |19              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Questions                               |Created                                         |20              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Regional_Instruments_id_seq"'::regclass)          |
|pejp04izqnshduq.Regional_Instruments                    |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Abbreviation                                    |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |URL                                             |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Attachment                                      |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Date                                            |12              |date                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |ID_Number                                       |13              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Created_By                                      |16              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Created                                         |17              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Instruments                    |Title                                           |18              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Regional_Legal_Provisions_id_seq"'::regclass)     |
|pejp04izqnshduq.Regional_Legal_Provisions               |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Title_of_the_Provision                          |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Full_Text                                       |10              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Provision                                       |11              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Interface_Order                                 |12              |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Arbitral_Awards                                 |13              |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Last_Modified                                   |14              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Last_Modified_By                                |15              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Created_By                                      |16              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Regional_Legal_Provisions               |Created                                         |17              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Specialists_id_seq"'::regclass)                   |
|pejp04izqnshduq.Specialists                             |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |Specialist                                      |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |Last_Modified                                   |10              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |Last_Modified_By                                |11              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |Created_By                                      |12              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Specialists                             |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Themes_id_seq"'::regclass)                        |
|pejp04izqnshduq.Themes                                  |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |Theme                                           |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |Last_Modified_By                                |10              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |Last_Modified                                   |11              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |Created_By                                      |12              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Themes                                  |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |id                                              |1               |integer                    |NO         |nextval('pejp04izqnshduq."Topics_id_seq"'::regclass)                        |
|pejp04izqnshduq.Topics                                  |created_at                                      |2               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |updated_at                                      |3               |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |updated_by                                      |5               |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |nc_order                                        |6               |numeric                    |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |ncRecordId                                      |7               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |ncRecordHash                                    |8               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |Topic                                           |9               |text                       |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |Last_Modified_By                                |10              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |Last_Modified                                   |11              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |Created_By                                      |12              |character varying          |YES        |NULL                                                                        |
|pejp04izqnshduq.Topics                                  |Created                                         |13              |timestamp without time zone|YES        |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Jurisdictions_Court_Decisions   |Court_Decisions_id                              |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Jurisdictions_Court_Decisions   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Jurisdictions_Domestic_Instru   |Domestic_Instruments_id                         |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Jurisdictions_Domestic_Instru   |Jurisdictions_id                                |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Arbitral_Awards          |Arbitral_Awards_id                              |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Arbitral_Awards          |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Domestic_Legal_          |Domestic_Legal_Provisions_id                    |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Domestic_Legal_          |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_HCCH_Answers             |HCCH_Answers_id                                 |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_HCCH_Answers             |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Literature               |Literature_id                                   |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Literature               |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Questions                |Questions_id                                    |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Questions                |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Topics                   |Topics_id                                       |1               |integer                    |NO         |NULL                                                                        |
|pejp04izqnshduq._nc_m2m_Themes_Topics                   |Themes_id                                       |2               |integer                    |NO         |NULL                                                                        |
|public.nc_api_tokens                                    |id                                              |1               |integer                    |NO         |nextval('nc_api_tokens_id_seq'::regclass)                                   |
|public.nc_api_tokens                                    |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |db_alias                                        |3               |character varying          |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |description                                     |4               |character varying          |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |permissions                                     |5               |text                       |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |token                                           |6               |text                       |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |expiry                                          |7               |character varying          |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |enabled                                         |8               |boolean                    |YES        |true                                                                        |
|public.nc_api_tokens                                    |created_at                                      |9               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |updated_at                                      |10              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_api_tokens                                    |fk_user_id                                      |11              |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_audit_v2                                      |user                                            |2               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |ip                                              |3               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |source_id                                       |4               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |base_id                                         |5               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |fk_model_id                                     |6               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |row_id                                          |7               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |op_type                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |op_sub_type                                     |9               |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |status                                          |10              |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |description                                     |11              |text                       |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |details                                         |12              |text                       |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |created_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_audit_v2                                      |updated_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_audit_v2                                      |version                                         |15              |smallint                   |YES        |'0'::smallint                                                               |
|public.nc_audit_v2                                      |fk_user_id                                      |16              |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |fk_ref_id                                       |17              |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |fk_parent_id                                    |18              |character varying          |YES        |NULL                                                                        |
|public.nc_audit_v2                                      |user_agent                                      |19              |text                       |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |base_id                                         |1               |character varying          |NO         |NULL                                                                        |
|public.nc_base_users_v2                                 |fk_user_id                                      |2               |character varying          |NO         |NULL                                                                        |
|public.nc_base_users_v2                                 |roles                                           |3               |text                       |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |starred                                         |4               |boolean                    |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |pinned                                          |5               |boolean                    |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |group                                           |6               |character varying          |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |color                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |order                                           |8               |real                       |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |hidden                                          |9               |real                       |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |opened_date                                     |10              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_base_users_v2                                 |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_base_users_v2                                 |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_base_users_v2                                 |invited_by                                      |13              |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_bases_v2                                      |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |prefix                                          |3               |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |status                                          |4               |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |description                                     |5               |text                       |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |meta                                            |6               |text                       |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |color                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |uuid                                            |8               |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |password                                        |9               |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |roles                                           |10              |character varying          |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |deleted                                         |11              |boolean                    |YES        |false                                                                       |
|public.nc_bases_v2                                      |is_meta                                         |12              |boolean                    |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |order                                           |13              |real                       |YES        |NULL                                                                        |
|public.nc_bases_v2                                      |created_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_bases_v2                                      |updated_at                                      |15              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_calendar_view_columns_v2                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |source_id                                       |3               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |show                                            |6               |boolean                    |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |bold                                            |7               |boolean                    |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |underline                                       |8               |boolean                    |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |italic                                          |9               |boolean                    |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |order                                           |10              |real                       |YES        |NULL                                                                        |
|public.nc_calendar_view_columns_v2                      |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_calendar_view_columns_v2                      |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_calendar_view_range_v2                        |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_calendar_view_range_v2                        |fk_view_id                                      |2               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_range_v2                        |fk_to_column_id                                 |3               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_range_v2                        |label                                           |4               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_range_v2                        |fk_from_column_id                               |5               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_range_v2                        |created_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_calendar_view_range_v2                        |updated_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_calendar_view_range_v2                        |base_id                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |fk_view_id                                      |1               |character varying          |NO         |NULL                                                                        |
|public.nc_calendar_view_v2                              |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |source_id                                       |3               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |title                                           |4               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |fk_cover_image_col_id                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |meta                                            |6               |text                       |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |created_at                                      |7               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_calendar_view_v2                              |updated_at                                      |8               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_col_barcode_v2                                |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_barcode_v2                                |fk_column_id                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_barcode_v2                                |fk_barcode_value_column_id                      |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_barcode_v2                                |barcode_format                                  |4               |character varying          |YES        |NULL                                                                        |
|public.nc_col_barcode_v2                                |deleted                                         |5               |boolean                    |YES        |NULL                                                                        |
|public.nc_col_barcode_v2                                |created_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_barcode_v2                                |updated_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_barcode_v2                                |base_id                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_button_v2                                 |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |type                                            |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |label                                           |4               |text                       |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |theme                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |color                                           |6               |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |icon                                            |7               |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |formula                                         |8               |text                       |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |formula_raw                                     |9               |text                       |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |error                                           |10              |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |parsed_tree                                     |11              |text                       |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |fk_webhook_id                                   |12              |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |fk_column_id                                    |13              |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |created_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_button_v2                                 |updated_at                                      |15              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_button_v2                                 |fk_integration_id                               |16              |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |model                                           |17              |character varying          |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |output_column_ids                               |18              |text                       |YES        |NULL                                                                        |
|public.nc_col_button_v2                                 |fk_workspace_id                                 |19              |character varying          |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_formula_v2                                |fk_column_id                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |formula                                         |3               |text                       |NO         |NULL                                                                        |
|public.nc_col_formula_v2                                |formula_raw                                     |4               |text                       |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |error                                           |5               |text                       |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |deleted                                         |6               |boolean                    |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |order                                           |7               |real                       |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |created_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_formula_v2                                |updated_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_formula_v2                                |parsed_tree                                     |10              |text                       |YES        |NULL                                                                        |
|public.nc_col_formula_v2                                |base_id                                         |11              |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_long_text_v2                              |fk_workspace_id                                 |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |fk_model_id                                     |4               |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |fk_integration_id                               |6               |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |model                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |prompt                                          |8               |text                       |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |prompt_raw                                      |9               |text                       |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |error                                           |10              |text                       |YES        |NULL                                                                        |
|public.nc_col_long_text_v2                              |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_long_text_v2                              |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_lookup_v2                                 |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_lookup_v2                                 |fk_column_id                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_lookup_v2                                 |fk_relation_column_id                           |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_lookup_v2                                 |fk_lookup_column_id                             |4               |character varying          |YES        |NULL                                                                        |
|public.nc_col_lookup_v2                                 |deleted                                         |5               |boolean                    |YES        |NULL                                                                        |
|public.nc_col_lookup_v2                                 |created_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_lookup_v2                                 |updated_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_lookup_v2                                 |base_id                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_col_qrcode_v2                                 |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_qrcode_v2                                 |fk_column_id                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_qrcode_v2                                 |fk_qr_value_column_id                           |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_qrcode_v2                                 |deleted                                         |4               |boolean                    |YES        |NULL                                                                        |
|public.nc_col_qrcode_v2                                 |order                                           |5               |real                       |YES        |NULL                                                                        |
|public.nc_col_qrcode_v2                                 |created_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_qrcode_v2                                 |updated_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_qrcode_v2                                 |base_id                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_relations_v2                              |ref_db_alias                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |type                                            |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |virtual                                         |4               |boolean                    |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |db_type                                         |5               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_column_id                                    |6               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_related_model_id                             |7               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_child_column_id                              |8               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_parent_column_id                             |9               |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_mm_model_id                                  |10              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_mm_child_column_id                           |11              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_mm_parent_column_id                          |12              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |ur                                              |13              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |dr                                              |14              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_index_name                                   |15              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |deleted                                         |16              |boolean                    |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |created_at                                      |17              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_relations_v2                              |updated_at                                      |18              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_relations_v2                              |fk_target_view_id                               |19              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |base_id                                         |20              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_related_base_id                              |21              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_mm_base_id                                   |22              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_related_source_id                            |23              |character varying          |YES        |NULL                                                                        |
|public.nc_col_relations_v2                              |fk_mm_source_id                                 |24              |character varying          |YES        |NULL                                                                        |
|public.nc_col_rollup_v2                                 |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_rollup_v2                                 |fk_column_id                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_rollup_v2                                 |fk_relation_column_id                           |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_rollup_v2                                 |fk_rollup_column_id                             |4               |character varying          |YES        |NULL                                                                        |
|public.nc_col_rollup_v2                                 |rollup_function                                 |5               |character varying          |YES        |NULL                                                                        |
|public.nc_col_rollup_v2                                 |deleted                                         |6               |boolean                    |YES        |NULL                                                                        |
|public.nc_col_rollup_v2                                 |created_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_rollup_v2                                 |updated_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_rollup_v2                                 |base_id                                         |9               |character varying          |YES        |NULL                                                                        |
|public.nc_col_select_options_v2                         |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_col_select_options_v2                         |fk_column_id                                    |2               |character varying          |YES        |NULL                                                                        |
|public.nc_col_select_options_v2                         |title                                           |3               |character varying          |YES        |NULL                                                                        |
|public.nc_col_select_options_v2                         |color                                           |4               |character varying          |YES        |NULL                                                                        |
|public.nc_col_select_options_v2                         |order                                           |5               |real                       |YES        |NULL                                                                        |
|public.nc_col_select_options_v2                         |created_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_select_options_v2                         |updated_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_col_select_options_v2                         |base_id                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_columns_v2                                    |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |fk_model_id                                     |4               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |title                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |column_name                                     |6               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |uidt                                            |7               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |dt                                              |8               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |np                                              |9               |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |ns                                              |10              |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |clen                                            |11              |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |cop                                             |12              |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |pk                                              |13              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |pv                                              |14              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |rqd                                             |15              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |un                                              |16              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |ct                                              |17              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |ai                                              |18              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |unique                                          |19              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |cdf                                             |20              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |cc                                              |21              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |csn                                             |22              |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |dtx                                             |23              |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |dtxp                                            |24              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |dtxs                                            |25              |character varying          |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |au                                              |26              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |validate                                        |27              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |virtual                                         |28              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |deleted                                         |29              |boolean                    |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |system                                          |30              |boolean                    |YES        |false                                                                       |
|public.nc_columns_v2                                    |order                                           |31              |real                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |created_at                                      |32              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_columns_v2                                    |updated_at                                      |33              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_columns_v2                                    |meta                                            |34              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |description                                     |35              |text                       |YES        |NULL                                                                        |
|public.nc_columns_v2                                    |readonly                                        |36              |boolean                    |YES        |false                                                                       |
|public.nc_columns_v2                                    |custom_index_name                               |37              |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_comment_reactions                             |row_id                                          |2               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |comment_id                                      |3               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |source_id                                       |4               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |fk_model_id                                     |5               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |base_id                                         |6               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |reaction                                        |7               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |created_by                                      |8               |character varying          |YES        |NULL                                                                        |
|public.nc_comment_reactions                             |created_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_comment_reactions                             |updated_at                                      |10              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_comments                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_comments                                      |row_id                                          |2               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |comment                                         |3               |text                       |YES        |NULL                                                                        |
|public.nc_comments                                      |created_by                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |created_by_email                                |5               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |resolved_by                                     |6               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |resolved_by_email                               |7               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |parent_comment_id                               |8               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |source_id                                       |9               |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |base_id                                         |10              |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |fk_model_id                                     |11              |character varying          |YES        |NULL                                                                        |
|public.nc_comments                                      |is_deleted                                      |12              |boolean                    |YES        |NULL                                                                        |
|public.nc_comments                                      |created_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_comments                                      |updated_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_data_reflection                               |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_data_reflection                               |fk_workspace_id                                 |2               |character varying          |YES        |NULL                                                                        |
|public.nc_data_reflection                               |username                                        |3               |character varying          |YES        |NULL                                                                        |
|public.nc_data_reflection                               |password                                        |4               |character varying          |YES        |NULL                                                                        |
|public.nc_data_reflection                               |database                                        |5               |character varying          |YES        |NULL                                                                        |
|public.nc_data_reflection                               |created_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_data_reflection                               |updated_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_disabled_models_for_role_v2                   |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_disabled_models_for_role_v2                   |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_disabled_models_for_role_v2                   |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_disabled_models_for_role_v2                   |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_disabled_models_for_role_v2                   |role                                            |5               |character varying          |YES        |NULL                                                                        |
|public.nc_disabled_models_for_role_v2                   |disabled                                        |6               |boolean                    |YES        |true                                                                        |
|public.nc_disabled_models_for_role_v2                   |created_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_disabled_models_for_role_v2                   |updated_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_extensions                                    |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_extensions                                    |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_extensions                                    |fk_user_id                                      |3               |character varying          |YES        |NULL                                                                        |
|public.nc_extensions                                    |extension_id                                    |4               |character varying          |YES        |NULL                                                                        |
|public.nc_extensions                                    |title                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_extensions                                    |kv_store                                        |6               |text                       |YES        |NULL                                                                        |
|public.nc_extensions                                    |meta                                            |7               |text                       |YES        |NULL                                                                        |
|public.nc_extensions                                    |order                                           |8               |real                       |YES        |NULL                                                                        |
|public.nc_extensions                                    |created_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_extensions                                    |updated_at                                      |10              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_file_references                               |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_file_references                               |storage                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |file_url                                        |3               |text                       |YES        |NULL                                                                        |
|public.nc_file_references                               |file_size                                       |4               |integer                    |YES        |NULL                                                                        |
|public.nc_file_references                               |fk_user_id                                      |5               |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |fk_workspace_id                                 |6               |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |base_id                                         |7               |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |source_id                                       |8               |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |fk_model_id                                     |9               |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |fk_column_id                                    |10              |character varying          |YES        |NULL                                                                        |
|public.nc_file_references                               |is_external                                     |11              |boolean                    |YES        |false                                                                       |
|public.nc_file_references                               |deleted                                         |12              |boolean                    |YES        |false                                                                       |
|public.nc_file_references                               |created_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_file_references                               |updated_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_filter_exp_v2                                 |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_filter_exp_v2                                 |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_hook_id                                      |5               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_column_id                                    |6               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_parent_id                                    |7               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |logical_op                                      |8               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |comparison_op                                   |9               |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |value                                           |10              |text                       |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |is_group                                        |11              |boolean                    |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |order                                           |12              |real                       |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |created_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_filter_exp_v2                                 |updated_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_filter_exp_v2                                 |comparison_sub_op                               |15              |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_link_col_id                                  |16              |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_value_col_id                                 |17              |character varying          |YES        |NULL                                                                        |
|public.nc_filter_exp_v2                                 |fk_parent_column_id                             |18              |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_form_view_columns_v2                          |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |uuid                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |label                                           |7               |text                       |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |help                                            |8               |text                       |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |description                                     |9               |text                       |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |required                                        |10              |boolean                    |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |show                                            |11              |boolean                    |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |order                                           |12              |real                       |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |created_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_form_view_columns_v2                          |updated_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_form_view_columns_v2                          |meta                                            |15              |text                       |YES        |NULL                                                                        |
|public.nc_form_view_columns_v2                          |enable_scanner                                  |16              |boolean                    |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |source_id                                       |1               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |fk_view_id                                      |3               |character varying          |NO         |NULL                                                                        |
|public.nc_form_view_v2                                  |heading                                         |4               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |subheading                                      |5               |text                       |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |success_msg                                     |6               |text                       |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |redirect_url                                    |7               |text                       |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |redirect_after_secs                             |8               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |email                                           |9               |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |submit_another_form                             |10              |boolean                    |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |show_blank_form                                 |11              |boolean                    |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |uuid                                            |12              |character varying          |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |banner_image_url                                |13              |text                       |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |logo_url                                        |14              |text                       |YES        |NULL                                                                        |
|public.nc_form_view_v2                                  |created_at                                      |15              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_form_view_v2                                  |updated_at                                      |16              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_form_view_v2                                  |meta                                            |17              |text                       |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |uuid                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |label                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |help                                            |8               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |show                                            |9               |boolean                    |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |order                                           |10              |real                       |YES        |NULL                                                                        |
|public.nc_gallery_view_columns_v2                       |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_gallery_view_columns_v2                       |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_gallery_view_v2                               |source_id                                       |1               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |fk_view_id                                      |3               |character varying          |NO         |NULL                                                                        |
|public.nc_gallery_view_v2                               |next_enabled                                    |4               |boolean                    |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |prev_enabled                                    |5               |boolean                    |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |cover_image_idx                                 |6               |integer                    |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |fk_cover_image_col_id                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |cover_image                                     |8               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |restrict_types                                  |9               |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |restrict_size                                   |10              |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |restrict_number                                 |11              |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |public                                          |12              |boolean                    |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |dimensions                                      |13              |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |responsive_columns                              |14              |character varying          |YES        |NULL                                                                        |
|public.nc_gallery_view_v2                               |created_at                                      |15              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_gallery_view_v2                               |updated_at                                      |16              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_gallery_view_v2                               |meta                                            |17              |text                       |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |fk_view_id                                      |2               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |fk_column_id                                    |3               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |source_id                                       |4               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |base_id                                         |5               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |uuid                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |label                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |help                                            |8               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |width                                           |9               |character varying          |YES        |'200px'::character varying                                                  |
|public.nc_grid_view_columns_v2                          |show                                            |10              |boolean                    |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |order                                           |11              |real                       |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |created_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_grid_view_columns_v2                          |updated_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_grid_view_columns_v2                          |group_by                                        |14              |boolean                    |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |group_by_order                                  |15              |real                       |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |group_by_sort                                   |16              |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_columns_v2                          |aggregation                                     |17              |character varying          |YES        |NULL::character varying                                                     |
|public.nc_grid_view_v2                                  |fk_view_id                                      |1               |character varying          |NO         |NULL                                                                        |
|public.nc_grid_view_v2                                  |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_v2                                  |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_v2                                  |uuid                                            |4               |character varying          |YES        |NULL                                                                        |
|public.nc_grid_view_v2                                  |created_at                                      |5               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_grid_view_v2                                  |updated_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_grid_view_v2                                  |meta                                            |7               |text                       |YES        |NULL                                                                        |
|public.nc_grid_view_v2                                  |row_height                                      |8               |integer                    |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_hook_logs_v2                                  |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |fk_hook_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |type                                            |5               |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |event                                           |6               |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |operation                                       |7               |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |test_call                                       |8               |boolean                    |YES        |true                                                                        |
|public.nc_hook_logs_v2                                  |payload                                         |9               |text                       |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |conditions                                      |10              |text                       |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |notification                                    |11              |text                       |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |error_code                                      |12              |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |error_message                                   |13              |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |error                                           |14              |text                       |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |execution_time                                  |15              |integer                    |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |response                                        |16              |text                       |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |triggered_by                                    |17              |character varying          |YES        |NULL                                                                        |
|public.nc_hook_logs_v2                                  |created_at                                      |18              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_hook_logs_v2                                  |updated_at                                      |19              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_hooks_v2                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_hooks_v2                                      |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |fk_model_id                                     |4               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |title                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |description                                     |6               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |env                                             |7               |character varying          |YES        |'all'::character varying                                                    |
|public.nc_hooks_v2                                      |type                                            |8               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |event                                           |9               |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |operation                                       |10              |character varying          |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |async                                           |11              |boolean                    |YES        |false                                                                       |
|public.nc_hooks_v2                                      |payload                                         |12              |boolean                    |YES        |true                                                                        |
|public.nc_hooks_v2                                      |url                                             |13              |text                       |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |headers                                         |14              |text                       |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |condition                                       |15              |boolean                    |YES        |false                                                                       |
|public.nc_hooks_v2                                      |notification                                    |16              |text                       |YES        |NULL                                                                        |
|public.nc_hooks_v2                                      |retries                                         |17              |integer                    |YES        |0                                                                           |
|public.nc_hooks_v2                                      |retry_interval                                  |18              |integer                    |YES        |60000                                                                       |
|public.nc_hooks_v2                                      |timeout                                         |19              |integer                    |YES        |60000                                                                       |
|public.nc_hooks_v2                                      |active                                          |20              |boolean                    |YES        |true                                                                        |
|public.nc_hooks_v2                                      |created_at                                      |21              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_hooks_v2                                      |updated_at                                      |22              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_hooks_v2                                      |version                                         |23              |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_integrations_store_v2                         |fk_integration_id                               |2               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |type                                            |3               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |sub_type                                        |4               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |fk_workspace_id                                 |5               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |fk_user_id                                      |6               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |created_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_integrations_store_v2                         |updated_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_integrations_store_v2                         |slot_0                                          |9               |text                       |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_1                                          |10              |text                       |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_2                                          |11              |text                       |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_3                                          |12              |text                       |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_4                                          |13              |text                       |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_5                                          |14              |integer                    |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_6                                          |15              |integer                    |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_7                                          |16              |integer                    |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_8                                          |17              |integer                    |YES        |NULL                                                                        |
|public.nc_integrations_store_v2                         |slot_9                                          |18              |integer                    |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_integrations_v2                               |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |config                                          |3               |text                       |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |meta                                            |4               |text                       |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |type                                            |5               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |sub_type                                        |6               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |is_private                                      |7               |boolean                    |YES        |false                                                                       |
|public.nc_integrations_v2                               |deleted                                         |8               |boolean                    |YES        |false                                                                       |
|public.nc_integrations_v2                               |created_by                                      |9               |character varying          |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |order                                           |10              |real                       |YES        |NULL                                                                        |
|public.nc_integrations_v2                               |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_integrations_v2                               |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_integrations_v2                               |is_default                                      |13              |boolean                    |YES        |false                                                                       |
|public.nc_integrations_v2                               |is_encrypted                                    |14              |boolean                    |YES        |false                                                                       |
|public.nc_jobs                                          |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_jobs                                          |job                                             |2               |character varying          |YES        |NULL                                                                        |
|public.nc_jobs                                          |status                                          |3               |character varying          |YES        |NULL                                                                        |
|public.nc_jobs                                          |result                                          |4               |text                       |YES        |NULL                                                                        |
|public.nc_jobs                                          |fk_user_id                                      |5               |character varying          |YES        |NULL                                                                        |
|public.nc_jobs                                          |fk_workspace_id                                 |6               |character varying          |YES        |NULL                                                                        |
|public.nc_jobs                                          |base_id                                         |7               |character varying          |YES        |NULL                                                                        |
|public.nc_jobs                                          |created_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_jobs                                          |updated_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_kanban_view_columns_v2                        |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |uuid                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |label                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |help                                            |8               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |show                                            |9               |boolean                    |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |order                                           |10              |real                       |YES        |NULL                                                                        |
|public.nc_kanban_view_columns_v2                        |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_kanban_view_columns_v2                        |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_kanban_view_v2                                |fk_view_id                                      |1               |character varying          |NO         |NULL                                                                        |
|public.nc_kanban_view_v2                                |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |show                                            |4               |boolean                    |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |order                                           |5               |real                       |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |uuid                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |title                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |public                                          |8               |boolean                    |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |password                                        |9               |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |show_all_fields                                 |10              |boolean                    |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_kanban_view_v2                                |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_kanban_view_v2                                |fk_grp_col_id                                   |13              |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |fk_cover_image_col_id                           |14              |character varying          |YES        |NULL                                                                        |
|public.nc_kanban_view_v2                                |meta                                            |15              |text                       |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_map_view_columns_v2                           |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |project_id                                      |3               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |uuid                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |label                                           |7               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |help                                            |8               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |show                                            |9               |boolean                    |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |order                                           |10              |real                       |YES        |NULL                                                                        |
|public.nc_map_view_columns_v2                           |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_map_view_columns_v2                           |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_map_view_v2                                   |fk_view_id                                      |1               |character varying          |NO         |NULL                                                                        |
|public.nc_map_view_v2                                   |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |uuid                                            |4               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |title                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |fk_geo_data_col_id                              |6               |character varying          |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |meta                                            |7               |text                       |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |created_at                                      |8               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_map_view_v2                                   |updated_at                                      |9               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_mcp_tokens                                    |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |token                                           |4               |character varying          |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |fk_workspace_id                                 |5               |character varying          |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |order                                           |6               |real                       |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |fk_user_id                                      |7               |character varying          |YES        |NULL                                                                        |
|public.nc_mcp_tokens                                    |created_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_mcp_tokens                                    |updated_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_models_v2                                     |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_models_v2                                     |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_models_v2                                     |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_models_v2                                     |table_name                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_models_v2                                     |title                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_models_v2                                     |type                                            |6               |character varying          |YES        |'table'::character varying                                                  |
|public.nc_models_v2                                     |meta                                            |7               |text                       |YES        |NULL                                                                        |
|public.nc_models_v2                                     |schema                                          |8               |text                       |YES        |NULL                                                                        |
|public.nc_models_v2                                     |enabled                                         |9               |boolean                    |YES        |true                                                                        |
|public.nc_models_v2                                     |mm                                              |10              |boolean                    |YES        |false                                                                       |
|public.nc_models_v2                                     |tags                                            |11              |character varying          |YES        |NULL                                                                        |
|public.nc_models_v2                                     |pinned                                          |12              |boolean                    |YES        |NULL                                                                        |
|public.nc_models_v2                                     |deleted                                         |13              |boolean                    |YES        |NULL                                                                        |
|public.nc_models_v2                                     |order                                           |14              |real                       |YES        |NULL                                                                        |
|public.nc_models_v2                                     |created_at                                      |15              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_models_v2                                     |updated_at                                      |16              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_models_v2                                     |description                                     |17              |text                       |YES        |NULL                                                                        |
|public.nc_models_v2                                     |synced                                          |18              |boolean                    |YES        |false                                                                       |
|public.nc_orgs_v2                                       |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_orgs_v2                                       |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_orgs_v2                                       |created_at                                      |3               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_orgs_v2                                       |updated_at                                      |4               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_plugins_v2                                    |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_plugins_v2                                    |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |description                                     |3               |text                       |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |active                                          |4               |boolean                    |YES        |false                                                                       |
|public.nc_plugins_v2                                    |rating                                          |5               |real                       |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |version                                         |6               |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |docs                                            |7               |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |status                                          |8               |character varying          |YES        |'install'::character varying                                                |
|public.nc_plugins_v2                                    |status_details                                  |9               |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |logo                                            |10              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |icon                                            |11              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |tags                                            |12              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |category                                        |13              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |input_schema                                    |14              |text                       |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |input                                           |15              |text                       |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |creator                                         |16              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |creator_website                                 |17              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |price                                           |18              |character varying          |YES        |NULL                                                                        |
|public.nc_plugins_v2                                    |created_at                                      |19              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_plugins_v2                                    |updated_at                                      |20              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_shared_bases                                  |id                                              |1               |integer                    |NO         |nextval('nc_shared_bases_id_seq'::regclass)                                 |
|public.nc_shared_bases                                  |project_id                                      |2               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_bases                                  |db_alias                                        |3               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_bases                                  |roles                                           |4               |character varying          |YES        |'viewer'::character varying                                                 |
|public.nc_shared_bases                                  |shared_base_id                                  |5               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_bases                                  |enabled                                         |6               |boolean                    |YES        |true                                                                        |
|public.nc_shared_bases                                  |password                                        |7               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_bases                                  |created_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_shared_bases                                  |updated_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_shared_views_v2                               |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_shared_views_v2                               |fk_view_id                                      |2               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |meta                                            |3               |text                       |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |query_params                                    |4               |text                       |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |view_id                                         |5               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |show_all_fields                                 |6               |boolean                    |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |allow_copy                                      |7               |boolean                    |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |password                                        |8               |character varying          |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |deleted                                         |9               |boolean                    |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |order                                           |10              |real                       |YES        |NULL                                                                        |
|public.nc_shared_views_v2                               |created_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_shared_views_v2                               |updated_at                                      |12              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sort_v2                                       |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_sort_v2                                       |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_sort_v2                                       |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_sort_v2                                       |fk_view_id                                      |4               |character varying          |YES        |NULL                                                                        |
|public.nc_sort_v2                                       |fk_column_id                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_sort_v2                                       |direction                                       |6               |character varying          |YES        |'false'::character varying                                                  |
|public.nc_sort_v2                                       |order                                           |7               |real                       |YES        |NULL                                                                        |
|public.nc_sort_v2                                       |created_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sort_v2                                       |updated_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sources_v2                                    |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_sources_v2                                    |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |alias                                           |3               |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |config                                          |4               |text                       |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |meta                                            |5               |text                       |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |is_meta                                         |6               |boolean                    |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |type                                            |7               |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |inflection_column                               |8               |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |inflection_table                                |9               |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |created_at                                      |10              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sources_v2                                    |updated_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sources_v2                                    |enabled                                         |12              |boolean                    |YES        |true                                                                        |
|public.nc_sources_v2                                    |order                                           |13              |real                       |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |description                                     |14              |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |erd_uuid                                        |15              |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |deleted                                         |16              |boolean                    |YES        |false                                                                       |
|public.nc_sources_v2                                    |is_schema_readonly                              |17              |boolean                    |YES        |false                                                                       |
|public.nc_sources_v2                                    |is_data_readonly                                |18              |boolean                    |YES        |false                                                                       |
|public.nc_sources_v2                                    |fk_integration_id                               |19              |character varying          |YES        |NULL                                                                        |
|public.nc_sources_v2                                    |is_local                                        |20              |boolean                    |YES        |false                                                                       |
|public.nc_sources_v2                                    |is_encrypted                                    |21              |boolean                    |YES        |false                                                                       |
|public.nc_store                                         |id                                              |1               |integer                    |NO         |nextval('nc_store_id_seq'::regclass)                                        |
|public.nc_store                                         |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_store                                         |db_alias                                        |3               |character varying          |YES        |'db'::character varying                                                     |
|public.nc_store                                         |key                                             |4               |character varying          |YES        |NULL                                                                        |
|public.nc_store                                         |value                                           |5               |text                       |YES        |NULL                                                                        |
|public.nc_store                                         |type                                            |6               |character varying          |YES        |NULL                                                                        |
|public.nc_store                                         |env                                             |7               |character varying          |YES        |NULL                                                                        |
|public.nc_store                                         |tag                                             |8               |character varying          |YES        |NULL                                                                        |
|public.nc_store                                         |created_at                                      |9               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_store                                         |updated_at                                      |10              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_sync_configs                                  |fk_workspace_id                                 |2               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |fk_integration_id                               |4               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |fk_model_id                                     |5               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |sync_type                                       |6               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |sync_trigger                                    |7               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |sync_trigger_cron                               |8               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |sync_trigger_secret                             |9               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |sync_job_id                                     |10              |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |last_sync_at                                    |11              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |next_sync_at                                    |12              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |created_at                                      |13              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_configs                                  |updated_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_configs                                  |title                                           |15              |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |sync_category                                   |16              |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |fk_parent_sync_config_id                        |17              |character varying          |YES        |NULL                                                                        |
|public.nc_sync_configs                                  |on_delete_action                                |18              |character varying          |YES        |'mark_deleted'::character varying                                           |
|public.nc_sync_logs_v2                                  |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_sync_logs_v2                                  |base_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_logs_v2                                  |fk_sync_source_id                               |3               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_logs_v2                                  |time_taken                                      |4               |integer                    |YES        |NULL                                                                        |
|public.nc_sync_logs_v2                                  |status                                          |5               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_logs_v2                                  |status_details                                  |6               |text                       |YES        |NULL                                                                        |
|public.nc_sync_logs_v2                                  |created_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_logs_v2                                  |updated_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_mappings                                 |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_sync_mappings                                 |fk_workspace_id                                 |2               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_mappings                                 |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_mappings                                 |fk_sync_config_id                               |4               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_mappings                                 |target_table                                    |5               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_mappings                                 |fk_model_id                                     |6               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_mappings                                 |created_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_mappings                                 |updated_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_source_v2                                |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_sync_source_v2                                |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |type                                            |3               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |details                                         |4               |text                       |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |deleted                                         |5               |boolean                    |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |enabled                                         |6               |boolean                    |YES        |true                                                                        |
|public.nc_sync_source_v2                                |order                                           |7               |real                       |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |base_id                                         |8               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |fk_user_id                                      |9               |character varying          |YES        |NULL                                                                        |
|public.nc_sync_source_v2                                |created_at                                      |10              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_source_v2                                |updated_at                                      |11              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_sync_source_v2                                |source_id                                       |12              |character varying          |YES        |NULL                                                                        |
|public.nc_team_users_v2                                 |org_id                                          |1               |character varying          |YES        |NULL                                                                        |
|public.nc_team_users_v2                                 |user_id                                         |2               |character varying          |YES        |NULL                                                                        |
|public.nc_team_users_v2                                 |created_at                                      |3               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_team_users_v2                                 |updated_at                                      |4               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_teams_v2                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_teams_v2                                      |title                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_teams_v2                                      |org_id                                          |3               |character varying          |YES        |NULL                                                                        |
|public.nc_teams_v2                                      |created_at                                      |4               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_teams_v2                                      |updated_at                                      |5               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_user_comment_notifications_preference         |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |row_id                                          |2               |character varying          |YES        |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |user_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |fk_model_id                                     |4               |character varying          |YES        |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |source_id                                       |5               |character varying          |YES        |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |base_id                                         |6               |character varying          |YES        |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |preferences                                     |7               |character varying          |YES        |NULL                                                                        |
|public.nc_user_comment_notifications_preference         |created_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_user_comment_notifications_preference         |updated_at                                      |9               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_user_refresh_tokens                           |fk_user_id                                      |1               |character varying          |YES        |NULL                                                                        |
|public.nc_user_refresh_tokens                           |token                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_user_refresh_tokens                           |meta                                            |3               |text                       |YES        |NULL                                                                        |
|public.nc_user_refresh_tokens                           |expires_at                                      |4               |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_user_refresh_tokens                           |created_at                                      |5               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_user_refresh_tokens                           |updated_at                                      |6               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_users_v2                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_users_v2                                      |email                                           |2               |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |password                                        |3               |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |salt                                            |4               |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |invite_token                                    |9               |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |invite_token_expires                            |10              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |reset_password_expires                          |11              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_users_v2                                      |reset_password_token                            |12              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |email_verification_token                        |13              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |email_verified                                  |14              |boolean                    |YES        |NULL                                                                        |
|public.nc_users_v2                                      |roles                                           |15              |character varying          |YES        |'editor'::character varying                                                 |
|public.nc_users_v2                                      |created_at                                      |16              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_users_v2                                      |updated_at                                      |17              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_users_v2                                      |token_version                                   |18              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |display_name                                    |19              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |user_name                                       |20              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |blocked                                         |21              |boolean                    |YES        |false                                                                       |
|public.nc_users_v2                                      |blocked_reason                                  |22              |character varying          |YES        |NULL                                                                        |
|public.nc_users_v2                                      |deleted_at                                      |23              |timestamp with time zone   |YES        |NULL                                                                        |
|public.nc_users_v2                                      |is_deleted                                      |24              |boolean                    |YES        |false                                                                       |
|public.nc_users_v2                                      |meta                                            |25              |text                       |YES        |NULL                                                                        |
|public.nc_views_v2                                      |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.nc_views_v2                                      |source_id                                       |2               |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |base_id                                         |3               |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |fk_model_id                                     |4               |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |title                                           |5               |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |type                                            |6               |integer                    |YES        |NULL                                                                        |
|public.nc_views_v2                                      |is_default                                      |7               |boolean                    |YES        |NULL                                                                        |
|public.nc_views_v2                                      |show_system_fields                              |8               |boolean                    |YES        |NULL                                                                        |
|public.nc_views_v2                                      |lock_type                                       |9               |character varying          |YES        |'collaborative'::character varying                                          |
|public.nc_views_v2                                      |uuid                                            |10              |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |password                                        |11              |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |show                                            |12              |boolean                    |YES        |NULL                                                                        |
|public.nc_views_v2                                      |order                                           |13              |real                       |YES        |NULL                                                                        |
|public.nc_views_v2                                      |created_at                                      |14              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_views_v2                                      |updated_at                                      |15              |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.nc_views_v2                                      |meta                                            |16              |text                       |YES        |NULL                                                                        |
|public.nc_views_v2                                      |description                                     |17              |text                       |YES        |NULL                                                                        |
|public.nc_views_v2                                      |created_by                                      |18              |character varying          |YES        |NULL                                                                        |
|public.nc_views_v2                                      |owned_by                                        |19              |character varying          |YES        |NULL                                                                        |
|public.notification                                     |id                                              |1               |character varying          |NO         |NULL                                                                        |
|public.notification                                     |type                                            |2               |character varying          |YES        |NULL                                                                        |
|public.notification                                     |body                                            |3               |text                       |YES        |NULL                                                                        |
|public.notification                                     |is_read                                         |4               |boolean                    |YES        |false                                                                       |
|public.notification                                     |is_deleted                                      |5               |boolean                    |YES        |false                                                                       |
|public.notification                                     |fk_user_id                                      |6               |character varying          |YES        |NULL                                                                        |
|public.notification                                     |created_at                                      |7               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.notification                                     |updated_at                                      |8               |timestamp with time zone   |NO         |CURRENT_TIMESTAMP                                                           |
|public.xc_knex_migrations                               |id                                              |1               |integer                    |NO         |nextval('xc_knex_migrations_id_seq'::regclass)                              |
|public.xc_knex_migrations                               |name                                            |2               |character varying          |YES        |NULL                                                                        |
|public.xc_knex_migrations                               |batch                                           |3               |integer                    |YES        |NULL                                                                        |
|public.xc_knex_migrations                               |migration_time                                  |4               |timestamp with time zone   |YES        |NULL                                                                        |
|public.xc_knex_migrations_lock                          |index                                           |1               |integer                    |NO         |nextval('xc_knex_migrations_lock_index_seq'::regclass)                      |
|public.xc_knex_migrations_lock                          |is_locked                                       |2               |integer                    |YES        |NULL                                                                        |
|public.xc_knex_migrationsv2                             |id                                              |1               |integer                    |NO         |nextval('xc_knex_migrationsv2_id_seq'::regclass)                            |
|public.xc_knex_migrationsv2                             |name                                            |2               |character varying          |YES        |NULL                                                                        |
|public.xc_knex_migrationsv2                             |batch                                           |3               |integer                    |YES        |NULL                                                                        |
|public.xc_knex_migrationsv2                             |migration_time                                  |4               |timestamp with time zone   |YES        |NULL                                                                        |
|public.xc_knex_migrationsv2_lock                        |index                                           |1               |integer                    |NO         |nextval('xc_knex_migrationsv2_lock_index_seq'::regclass)                    |
|public.xc_knex_migrationsv2_lock                        |is_locked                                       |2               |integer                    |YES        |NULL                                                                        |
