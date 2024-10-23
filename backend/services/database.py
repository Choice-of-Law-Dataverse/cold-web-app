import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class Database:
    def __init__(self, connection_string):
        self.engine = sa.create_engine(f"{connection_string}")
        self.metadata = sa.MetaData()

        try:
            self.metadata.reflect(bind=self.engine)
        except SQLAlchemyError as e:
            print(f"Error reflecting metadata: {e}")
            self.metadata = None

        self.session = sessionmaker(bind=self.engine)()

    def get_all_entries(self):
        if not self.metadata:
            return None
        
        all_entries = {}
        try:
            for table_name, table in self.metadata.tables.items():
                query = table.select()
                result = self.session.execute(query)
                columns = result.keys()
                entries = [dict(zip(columns, row)) for row in result.fetchall()]
                all_entries[table_name] = entries
        except SQLAlchemyError as e:
            print(f"Error getting all entries: {e}")
        finally:
            self.session.close()
        return all_entries

    def get_entries_from_tables(self, list_of_tables):
        if not self.metadata:
            return None

        entries_from_tables = {}
        try:
            for table_name in list_of_tables:
                # Check if the table exists in the metadata
                if table_name in self.metadata.tables:
                    table = self.metadata.tables[table_name]
                    query = table.select()
                    result = self.session.execute(query)
                    columns = result.keys()
                    entries = [dict(zip(columns, row)) for row in result.fetchall()]
                    entries_from_tables[table_name] = entries
                else:
                    print(f"Table {table_name} does not exist in the database.")
        except SQLAlchemyError as e:
            print(f"Error getting entries from tables: {e}")
        finally:
            self.session.close()

        return entries_from_tables

    def get_entry_by_id(self, table_name, entry_id):
        if not self.metadata:
            return None
        
        # Map id column names to tables
        id_columns = {
            'Answers': 'ID',
            'Legislation': 'ID',
            'Legal provisions': 'Name',
            'Court decisions': 'ID'
        }

        entry = {}
        try:
            if table_name in self.metadata.tables:
                table = self.metadata.tables[table_name]
                if table_name in id_columns:
                    id_column = id_columns[table_name]
                    query = table.select().where(table.c[id_column] == entry_id)
                    result = self.session.execute(query)
                    
                    row = result.fetchone()
                    if row:
                        columns = result.keys()
                        entry = dict(zip(columns, row))
                    else:
                        print(f"No entry found with id {entry_id} in table {table_name}.")
                else:
                    print(f"Table {table_name} does not have a mapped id column.")
            else:
                print(f"Table {table_name} does not exist in the database.")
        except SQLAlchemyError as e:
            print(f"Error getting entry by id: {e}")
        finally:
            self.session.close()

        return entry

    def execute_query(self, query, params=None):
        """
        Execute a given SQL query and return the results as a list of dictionaries.
        
        Parameters:
        - query: SQLAlchemy text query or SQL string
        - params: Optional dictionary of query parameters
        
        Returns:
        - List of results as dictionaries
        """
        try:
            # Use the session to execute the query
            result = self.session.execute(sa.text(query), params or {})
            
            # Fetch all rows from the result
            rows = result.fetchall()
            
            # If there are no rows, return an empty list
            if not rows:
                return []

            # Get column names from the result
            columns = result.keys()
            
            # Convert the rows into a list of dictionaries
            results = [dict(zip(columns, row)) for row in rows]
            
            return results

        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            return None

        finally:
            self.session.close()
