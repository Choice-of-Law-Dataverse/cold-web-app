# import libraries
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POSTGRES_AZURE_DBNAME = os.getenv("POSTGRES_AZURE_DBNAME")
POSTGRES_AZURE_HOST = os.getenv("POSTGRES_AZURE_HOST")
POSTGRES_AZURE_USER = os.getenv("POSTGRES_AZURE_USER")
POSTGRES_AZURE_PASSWORD = os.getenv("POSTGRES_AZURE_PASSWORD")

# Functions
def execute_query(query):
    """
    Connects to a PostgreSQL database and executes a given SQL query.

    Args:
    query (str): SQL query to be executed.

    Returns:
    list of tuples: Query results.
    """
    # Database connection parameters
    host = POSTGRES_AZURE_HOST  # e.g., 'mydb.postgres.database.azure.com'
    dbname = POSTGRES_AZURE_DBNAME
    user = POSTGRES_AZURE_USER  # e.g., 'myusername@mydb'
    password = POSTGRES_AZURE_PASSWORD
    sslmode = "require"  # Azure requires SSL for PostgreSQL

    # Connection URI
    conn_string = f"dbname='{dbname}' user='{user}' host='{host}' password='{password}' sslmode='{sslmode}'"

    # Connect to the PostgreSQL server
    conn = psycopg2.connect(conn_string)
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)  # Execute the SQL query
                records = cur.fetchall()  # Fetch all the results¨
                #print("Records fetched:", records)
                return records
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()  # Ensure that the connection is closed

def search_all_tables(search_string):
    results = {}
    total_matches = 0  # Initialize a counter for the total number of matches

    search_terms = search_string.split()
    conn = psycopg2.connect(dbname=POSTGRES_AZURE_DBNAME, user=POSTGRES_AZURE_USER, password=POSTGRES_AZURE_PASSWORD, host=POSTGRES_AZURE_HOST, sslmode="require")
    cur = conn.cursor()

    try:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()

        for table in tables:
            table_name = table[0]
            cur.execute(sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = %s AND table_schema = 'public'"), (table_name,))
            columns = cur.fetchall()
            if not columns:
                continue

            term_query_parts = []
            for term in search_terms:
                column_conditions = [sql.SQL("CAST({} AS TEXT) ILIKE %s").format(sql.Identifier(column[0])) for column in columns]
                term_condition = sql.SQL(" OR ").join(column_conditions)
                term_query_parts.append(sql.SQL("(") + term_condition + sql.SQL(")"))

            full_query = sql.SQL(" AND ").join(term_query_parts)
            query = sql.SQL("SELECT * FROM {} WHERE ").format(sql.Identifier(table_name)) + full_query
            params = [f"%{term}%" for term in search_terms for _ in range(len(columns))]
            
            #print("Now executing:\n", query)
            cur.execute(query, params)
            rows = cur.fetchall()

            if rows:
                table_results = {
                    'matches': len(rows),
                    'results': []
                }
                for row in rows:
                    result_details = {col.name: row[idx] if isinstance(row[idx], (int, float, str, bool)) else str(row[idx]) for idx, col in enumerate(cur.description)}
                    table_results['results'].append(result_details)
                results[table_name] = table_results
                total_matches += len(rows)  # Increment the total_matches by the number of matches found
                
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

    # Wrap the total matches and all table results into a final JSON response
    final_results = {
        'total_matches': total_matches,
        'tables': results
    }
    return final_results  # Convert the dictionary to JSON format and return it

def list_to_dict(lst):
    """
    Converts a list of dictionaries into a dictionary using the index of each item in the list as the key.

    Args:
        lst (list): The list of dictionaries.

    Returns:
        dict: A dictionary where each key is the index of the item in the list and each value is the corresponding dictionary.
    """
    result_dict = {i: item for i, item in enumerate(lst)}
    return result_dict

def print_keys(nested_dict):
    """
    Recursively prints all keys from a nested dictionary.

    Args:
    nested_dict (dict): The dictionary from which to print keys.
    """
    for key, value in nested_dict.items():
        print(key)  # Print the key
        if type(value) == list:
            value = list_to_dict(value)
        if isinstance(value, dict):
            print_keys(value)  # Recursively call print_keys if the value is also a dictionary

def parse_results(nested_dict):
    """
    Recursively transforms lists into dictionaries within a nested dictionary structure and prints all keys.

    Args:
        nested_dict (dict): The dictionary to transform.

    Returns:
        dict: A new dictionary with lists transformed into dictionaries and all nested structures preserved.
    """
    transformed_dict = {}
    for key, value in nested_dict.items():
        if isinstance(value, list):  # Convert list to dict if the value is a list
            value = list_to_dict(value)
        if isinstance(value, dict):  # Recursively call if the value is a dictionary
            value = parse_results(value)
        transformed_dict[key] = value
    return transformed_dict

def filter_na(nested_dict):
    """
    Recursively filters out 'NA' and 'NaN' values from a nested dictionary,
    independent of their case (case-insensitive).

    Args:
        nested_dict (dict): The dictionary to filter.

    Returns:
        dict: A new dictionary with 'NA' and 'NaN' values filtered out.
    """
    filtered_dict = {}
    for key, value in nested_dict.items():
        # Convert value to string and check in a case-insensitive manner
        if isinstance(value, str) and value.strip().upper() in ["NA", "NAN"]:
            continue

        # Recursively apply filtering if the value is a dictionary
        if isinstance(value, dict):
            value = filter_na(value)

        # Only add the value to the new dictionary if it's not an empty dictionary
        if value or isinstance(value, (int, float, bool)) or (isinstance(value, dict) and value):
            filtered_dict[key] = value

    return filtered_dict

# Run
if __name__ == "__main__":
    # to run a specific sql query:
    #print(execute_query("SELECT * FROM questions;"))#"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
    # to test search_all_tables
    # define search string
    search_string = "submarine"
    # print keys of the nested dictionary
    #print_keys(search_all_tables(search_string))
    # print dict without NAs
    #print(filter_na(search_all_tables(search_string)))
    print(filter_na(parse_results(search_all_tables(search_string))))