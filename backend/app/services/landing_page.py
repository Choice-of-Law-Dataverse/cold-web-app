from app.services.database import Database
from app.config import config

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
