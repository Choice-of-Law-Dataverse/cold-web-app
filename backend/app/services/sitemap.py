from app.config import config
from app.services.database import Database


class SitemapService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.base_urls = {
            "beta": "https://www.cold.global",  # Production URL
            "alpha": "https://alpha.cold.global"  # Alpha URL
        }
        
        # Define the mapping between database tables and URL prefixes
        self.table_url_mapping = {
            "Answers": "question",
            "Literature": "literature", 
            "Regional_Instruments": "regional-instrument",
            "International_Instruments": "international-instrument",
            "Court_Decisions": "court-decision",
            "Domestic_Instruments": "domestic-instrument"
        }

    def get_all_frontend_urls(self):
        """
        Generate all possible frontend URLs by querying the database for all IDs
        and mapping them to their respective URL prefixes.
        """
        alpha_urls = []
        beta_urls = []
        
        for table_name, url_prefix in self.table_url_mapping.items():
            try:
                # Query the database to get all IDs for this table
                ids = self._get_table_ids(table_name)
                
                # Generate URLs for each ID for both environments
                for id_value in ids:
                    alpha_url = f"{self.base_urls['alpha']}/{url_prefix}/{id_value}"
                    beta_url = f"{self.base_urls['beta']}/{url_prefix}/{id_value}"
                    alpha_urls.append(alpha_url)
                    beta_urls.append(beta_url)
                    
            except Exception as e:
                print(f"Error processing table {table_name}: {e}")
                continue
        
        return {
            "alpha": {
                "urls": alpha_urls,
                "total_count": len(alpha_urls),
                "base_url": self.base_urls['alpha']
            },
            "beta": {
                "urls": beta_urls,
                "total_count": len(beta_urls),
                "base_url": self.base_urls['beta']
            },
            "tables_processed": list(self.table_url_mapping.keys())
        }
    
    def _get_table_ids(self, table_name):
        """
        Get all IDs from a specific table.
        """
        try:
            # Execute query to get all IDs from the table
            query = f'SELECT id FROM "{config.NOCODB_POSTGRES_SCHEMA}"."{table_name}" WHERE id IS NOT NULL ORDER BY id'
            result = self.db.execute_query(query)
            
            # Extract IDs from the result
            ids = []
            if result:
                for row in result:
                    if 'id' in row and row['id']:
                        ids.append(row['id'])

            return ids
        except Exception as e:
            print(f"Error getting IDs from table {table_name}: {e}")
            return []
