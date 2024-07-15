import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

class Database:
    def __init__(self, connection_string):
        self.engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        self.metadata = sa.MetaData()
        self.metadata.reflect(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def get_all_entries(self):
        all_entries = {}
        try:
            for table_name, table in self.metadata.tables.items():
                query = table.select()
                result = self.session.execute(query)
                columns = result.keys()
                entries = [dict(zip(columns, row)) for row in result.fetchall()]
                all_entries[table_name] = entries
        finally:
            self.session.close()
        return all_entries
