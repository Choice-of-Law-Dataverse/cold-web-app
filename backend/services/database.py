import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import time


class Database:
    def __init__(self, connection_string, max_retries=3, retry_delay=0.5):
        """
        Initialize the database module.

        Parameters:
        - connection_string: Database connection string.
        - max_retries: Maximum number of retries for fetching data.
        - retry_delay: Delay between retries in seconds.
        """
        self.engine = sa.create_engine(connection_string)
        self.metadata = sa.MetaData()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        try:
            self.metadata.reflect(bind=self.engine)
        except SQLAlchemyError as e:
            print(f"Error reflecting metadata: {e}")
            self.metadata = None

        self.Session = sessionmaker(bind=self.engine)

    def _retry_on_empty(self, func, *args, **kwargs):
        """
        Retry logic to handle cases where the database returns empty results.

        Parameters:
        - func: Function to call for fetching data.
        - args, kwargs: Arguments to pass to the function.

        Returns:
        - The result from the function or an empty list if retries are exhausted.
        """
        for attempt in range(self.max_retries):
            result = func(*args, **kwargs)
            if result:  # If data is found, return immediately
                return result
            time.sleep(self.retry_delay)  # Wait before retrying
        return result  # Return the final result after all retries

    def get_all_entries(self):
        if not self.metadata:
            return None

        def fetch_all_entries():
            all_entries = {}
            with self.Session() as session:
                try:
                    for table_name, table in self.metadata.tables.items():
                        query = table.select()
                        result = session.execute(query)
                        columns = result.keys()
                        entries = [dict(zip(columns, row)) for row in result.fetchall()]
                        all_entries[table_name] = entries
                except SQLAlchemyError as e:
                    print(f"Error getting all entries: {e}")
            return all_entries

        return self._retry_on_empty(fetch_all_entries)

    def get_entries_from_tables(self, list_of_tables):
        if not self.metadata:
            return None

        def fetch_entries():
            entries_from_tables = {}
            with self.Session() as session:
                try:
                    for table_name in list_of_tables:
                        if table_name in self.metadata.tables:
                            table = self.metadata.tables[table_name]
                            query = table.select()
                            result = session.execute(query)
                            columns = result.keys()
                            entries = [
                                dict(zip(columns, row)) for row in result.fetchall()
                            ]
                            entries_from_tables[table_name] = entries
                        else:
                            print(f"Table {table_name} does not exist in the database.")
                except SQLAlchemyError as e:
                    print(f"Error getting entries from tables: {e}")
            return entries_from_tables

        return self._retry_on_empty(fetch_entries)

    def get_entry_by_id(self, table_name, entry_id):
        if not self.metadata:
            return None

        id_columns = {
            "Answers": "ID",
            "Legislation": "ID",
            "Legal provisions": "Name",
            "Court decisions": "ID",
            "Jurisdictions": "Alpha-3 code",
            "Literature": "Key",
        }

        def fetch_entry():
            entry = {}
            with self.Session() as session:
                try:
                    if table_name in self.metadata.tables:
                        table = self.metadata.tables[table_name]
                        if table_name in id_columns:
                            id_column = id_columns[table_name]
                            query = table.select().where(table.c[id_column] == entry_id)
                            result = session.execute(query)

                            row = result.fetchone()
                            if row:
                                columns = result.keys()
                                entry = dict(zip(columns, row))
                            else:
                                print(
                                    f"No entry found with id {entry_id} in table {table_name}."
                                )
                                return {"error": "no entry found with the specified id"}
                        else:
                            print(
                                f"Table {table_name} does not have a mapped id column."
                            )
                    else:
                        print(f"Table {table_name} does not exist in the database.")
                except SQLAlchemyError as e:
                    print(f"Error getting entry by id: {e}")
            return entry

        return self._retry_on_empty(fetch_entry)

    def execute_query(self, query, params=None):
        def fetch_query():
            with self.Session() as session:
                try:
                    result = session.execute(sa.text(query), params or {})
                    rows = result.fetchall()
                    if not rows:
                        return []

                    columns = result.keys()
                    results = [dict(zip(columns, row)) for row in rows]
                    return results

                except SQLAlchemyError as e:
                    print(f"Error executing query: {e}")
                    return None

        return self._retry_on_empty(fetch_query)
