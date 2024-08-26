import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class Database:
    def __init__(self, connection_string):
        print(f"Connection string: {connection_string}")
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
