from app.config import config
from app.services.database import Database


class LandingPageService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.schema = config.NOCODB_POSTGRES_SCHEMA

    def get_jurisdictions(self):
        """
        Returns list of jurisdictions with has_data flag:
        1 if there are answers other than 'No data' for the jurisdiction, 0 otherwise.
        """
        query = f"""
        SELECT j."Alpha_3_Code" AS code,
               CASE WHEN COUNT(*) FILTER (WHERE a."Answer" != 'No data') > 0 THEN 1 ELSE 0 END AS has_data
        FROM "{self.schema}"."_nc_m2m_Jurisdictions_Answers" m
        JOIN "Answers" a ON a.id = m."Answers_id"
        JOIN "Jurisdictions" j ON j.id = m."Jurisdictions_id"
        GROUP BY j."Alpha_3_Code"
        """
        return self.db.execute_query(query)

    def count_by_jurisdiction(self, table_name: str):
        """
        Returns count of rows grouped by jurisdiction for the specified table.

        Args:
            table_name: The table name (e.g., 'Court_Decisions', 'Domestic_Instruments')

        Returns:
            List of dicts with jurisdiction name and count, ordered by count descending.
        """
        # Map of table names to their m2m link table names
        link_table_map = {
            "Court_Decisions": "_nc_m2m_Jurisdictions_Court_Decisions",
            "Domestic_Instruments": "_nc_m2m_Jurisdictions_Domestic_Instruments",
            "Literature": "_nc_m2m_Jurisdictions_Literature",
        }

        if table_name not in link_table_map:
            return []

        link_table = link_table_map[table_name]
        table_id_column = f"{table_name}_id"

        query = f"""
        SELECT j."Name" AS jurisdiction,
               COUNT(DISTINCT m."{table_id_column}") AS n
        FROM "{self.schema}"."{link_table}" m
        JOIN "{self.schema}"."Jurisdictions" j ON j.id = m."Jurisdictions_id"
        GROUP BY j."Name"
        ORDER BY n DESC
        """
        return self.db.execute_query(query)
