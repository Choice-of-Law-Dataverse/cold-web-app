from app.config import config
from app.schemas.responses import JurisdictionCount
from app.services.database import Database
from app.services.transformers import DataTransformerFactory


class StatisticsService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.schema = config.NOCODB_POSTGRES_SCHEMA

    def get_jurisdictions_with_answer_coverage(self) -> list[dict]:
        """
        Returns list of all jurisdictions with the percentage of answers that are not 'no data'.

        Returns:
            List of transformed dicts with all jurisdiction fields plus "Answer Coverage" (0-100).
        """
        query = f"""
        SELECT
            j.*,
            COALESCE(
                ROUND(
                    (COUNT(a.id) FILTER (WHERE LOWER(a."Answer") != 'no data') * 100.0) / NULLIF(COUNT(a.id), 0),
                    2
                ),
                0
            ) AS "Answer_Coverage"
        FROM "{self.schema}"."Jurisdictions" j
        LEFT JOIN "{self.schema}"."_nc_m2m_Jurisdictions_Answers" m ON j.id = m."Jurisdictions_id"
        LEFT JOIN "{self.schema}"."Answers" a ON a.id = m."Answers_id"
        GROUP BY j.id
        ORDER BY j."Name"
        """
        results = self.db.execute_query(query)

        if not results:
            return []

        # Transform each jurisdiction record using DataTransformerFactory
        # This will convert field names like Alpha_3_Code to "Alpha-3 Code"
        # and Answer_Coverage to "Answer Coverage" using the mapping config
        transformed_results = []
        for row in results:
            transformed = DataTransformerFactory.transform_result("Jurisdictions", row)
            transformed_results.append(transformed)

        return transformed_results

    def count_by_jurisdiction(self, table_name: str, limit: int | None = None) -> list[JurisdictionCount]:
        """
        Returns count of rows grouped by jurisdiction for the specified table.

        Args:
            table_name: The table name (e.g., 'Court Decisions', 'Domestic Instruments', 'Literature')
            limit: Optional limit on number of results to return

        Returns:
            List of JurisdictionCount objects with jurisdiction name and count, ordered by count descending.
        """
        # Map frontend table names (with spaces) to database table names (with underscores)
        table_name_map = {
            "Court Decisions": "Court_Decisions",
            "Domestic Instruments": "Domestic_Instruments",
            "Literature": "Literature",
        }

        # Convert to database table name
        db_table_name = table_name_map.get(table_name, table_name.replace(" ", "_"))

        # Map of database table names to their m2m link table names
        link_table_map = {
            "Court_Decisions": "_nc_m2m_Jurisdictions_Court_Decisions",
            "Domestic_Instruments": "_nc_m2m_Jurisdictions_Domestic_Instruments",
            "Literature": "_nc_m2m_Jurisdictions_Literature",
        }

        if db_table_name not in link_table_map:
            return []

        link_table = link_table_map[db_table_name]
        table_id_column = f"{db_table_name}_id"

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
