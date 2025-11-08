from app.config import config
from app.schemas.responses import JurisdictionCount
from app.services.database import Database


class StatisticsService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.schema = config.NOCODB_POSTGRES_SCHEMA

    def count_by_jurisdiction(self, table_name: str, limit: int | None = None) -> list[JurisdictionCount]:
        """
        Returns count of rows grouped by jurisdiction for the specified table.

        Args:
            table_name: The table name (e.g., 'Court_Decisions', 'Domestic_Instruments')
            limit: Optional limit on number of results to return

        Returns:
            List of JurisdictionCount objects with jurisdiction name and count, ordered by count descending.
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

        limit_clause = f"LIMIT {limit}" if limit else ""

        query = f"""
        SELECT j."Name" AS jurisdiction,
               COUNT(DISTINCT m."{table_id_column}") AS n
        FROM "{self.schema}"."{link_table}" m
        JOIN "{self.schema}"."Jurisdictions" j ON j.id = m."Jurisdictions_id"
        GROUP BY j."Name"
        ORDER BY n DESC
        {limit_clause}
        """
        results = self.db.execute_query(query)
        return [JurisdictionCount(**row) for row in results] if results else []
