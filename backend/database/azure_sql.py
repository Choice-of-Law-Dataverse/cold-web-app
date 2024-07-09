import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

def get_engine(connection_string):
    """
    Create an SQLAlchemy engine.
    """
    engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
    return engine

def create_session(engine):
    """
    Create a new session with the provided SQLAlchemy engine.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def close_session(session):
    """
    Close the given session.
    """
    session.close()

def reflect_metadata(engine):
    """
    Reflect the existing database metadata.
    """
    metadata = sa.MetaData()
    metadata.reflect(bind=engine)
    return metadata

def query_data(session, query):
    """
    Execute a query and return the results.
    """
    result = session.execute(query)
    return result.fetchall()

class Database:
    def __init__(self, connection_string):
        self.engine = get_engine(connection_string)
        self.metadata = reflect_metadata(self.engine)
        self.session = create_session(self.engine)

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
            close_session(self.session)
        return all_entries
