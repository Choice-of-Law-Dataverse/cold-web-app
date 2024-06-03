# import libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import numpy as np
from mixedbread_ai.client import MixedbreadAI
from scipy.spatial.distance import cosine
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POSTGRES_AZURE_DBNAME = os.getenv("POSTGRES_AZURE_DBNAME")
POSTGRES_AZURE_HOST = os.getenv("POSTGRES_AZURE_HOST")
POSTGRES_AZURE_USER = os.getenv("POSTGRES_AZURE_USER")
POSTGRES_AZURE_PASSWORD = os.getenv("POSTGRES_AZURE_PASSWORD")

# Create Flask app
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

def get_embedding_api(text):
        mxbai = MixedbreadAI(api_key=os.getenv("MIXEDBREAD_API_KEY"))

        embedding = mxbai.embeddings(
            model="mixedbread-ai/mxbai-embed-large-v1",
            input=[text],
            normalized=True,
            encoding_format='ubinary',
            dimensions=512,
            truncation_strategy='start',
            prompt="Represent this sentence for searching relevant passages"
        )

        # convert embedding to np.array
        embedding = np.array(embedding.data[0].embedding)

        return embedding

def search_all_tables(search_string):
    results = {}
    total_matches = 0  # Initialize a counter for the total number of matches

    search_terms = search_string.split()
    print(search_terms)
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

def search_all_tables_semantic(search_string):
    results = {}
    total_matches = 0  # Initialize a counter for the total number of matches

    # Calculate the embedding for the search string
    search_embedding = get_embedding_api(search_string)
    
    conn = psycopg2.connect(dbname=POSTGRES_AZURE_DBNAME, user=POSTGRES_AZURE_USER, password=POSTGRES_AZURE_PASSWORD, host=POSTGRES_AZURE_HOST, sslmode="require")
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT DISTINCT table_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND column_name = 'embedding'
        """)
        tables = cur.fetchall()

        for table in tables:
            table_name = table[0]

            # Select all rows from the table
            query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            cur.execute(query)
            rows = cur.fetchall()
            if not rows:
                continue

            for row in rows:
                row_dict = {cur.description[idx].name: row[idx] for idx in range(len(row))}
                row_embedding = np.fromstring(row_dict['embedding'][1:-1], sep=',')  # Convert the string embedding back to a numpy array
                
                # Calculate the cosine similarity
                similarity = 1 - cosine(search_embedding, row_embedding)
                
                if similarity > 0.9:  # Example threshold, adjust as needed
                    row_dict['similarity'] = similarity
                    row_dict['table_name'] = table_name  # Add table name to each result
                    if table_name not in results:
                        results[table_name] = {'matches': 0, 'results': []}
                    results[table_name]['results'].append(row_dict)
                    results[table_name]['matches'] += 1
                    total_matches += 1
                
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return {'error': str(e)}, 500
    finally:
        cur.close()
        conn.close()

   # Wrap the total matches and all table results into a final JSON response
    final_results = {
        'total_matches': total_matches,
        'tables': results
    }
    return final_results  # Convert the dictionary to JSON format and return it

def search_selected_tables(search_string, filter_string):
    results = {}
    total_matches = 0  # Initialize a counter for the total number of matches

    search_terms = search_string.split()
    filter_tables = filter_string.split(',')
    print(search_terms)
    print(filter_tables)
    conn = psycopg2.connect(dbname=POSTGRES_AZURE_DBNAME, user=POSTGRES_AZURE_USER, password=POSTGRES_AZURE_PASSWORD, host=POSTGRES_AZURE_HOST, sslmode="require")
    cur = conn.cursor()

    try:
        sql_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = ANY(%s)"
        cur.execute(sql_query, (filter_tables,))
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

def check_tables():
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_AZURE_DBNAME,
            user=POSTGRES_AZURE_USER,
            password=POSTGRES_AZURE_PASSWORD,
            host=POSTGRES_AZURE_HOST
        )
        cur = conn.cursor()
        #cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_type='BASE TABLE'")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cur.fetchall()
        for table in tables:
            print(table)
        cur.close()
        conn.close()
    except Exception as e:
        print("Failed to fetch tables:", e)

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

# Function to flatten and transform the data
def flatten_and_transform_data(data):
    flattened_data = []
    
    def flatten_json(nested_json, parent_key='', sep='_'):
        items = []
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(flatten_json({f"{new_key}{sep}{i}": item}, '', sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    for table_name, table_data in data['tables'].items():
        for result_key, result_data in table_data['results'].items():
            flattened_result = flatten_json(result_data)
            flattened_result['table'] = table_name  # Add the table name as a new key
            flattened_data.append(flattened_result)
    
    return flattened_data

def sort_by_similarity(results):
    """
    Args:
        results (dict): The results dictionary containing tables with their respective results.

    Returns:
        list: A sorted list of all entries by similarity.
    """
    # Sort the flattened list by similarity in descending order
    sorted_results = sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)
    return sorted_results

@app.route('/search', methods=['POST'])
def handle_search():
    """
    Handle search operations from HTTP POST request.
    Expects data with a 'search_string' key and optionally 'filter_string'.
    """
    data = request.json
    search_string = data.get('search_string')
    filter_string = data.get('filter_string')
    use_semantic_search = data.get('use_semantic_search', False)
    print(search_string)
    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400
    if use_semantic_search:
        results = filter_na(parse_results(search_all_tables_semantic(search_string)))
        sorted_results = sort_by_similarity(flatten_and_transform_data(results))  # Flatten and sort results by similarity
        return jsonify({'results': sorted_results, 'total_matches': len(sorted_results)}), 200
    else:
        if filter_string:
            print(filter_string)
            results = filter_na(parse_results(search_selected_tables(search_string, filter_string)))
        else:
            results = filter_na(parse_results(search_all_tables(search_string)))
        sorted_results = results  # No need to flatten and sort for non-semantic search
        return results, 200

if __name__ == "__main__":
    app.run(debug=True)
