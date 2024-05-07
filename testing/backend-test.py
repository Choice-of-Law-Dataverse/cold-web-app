# import libraries
from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
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



@app.route('/search', methods=['POST'])
def handle_search():
    """
    Handle search operations from HTTP POST request.
    Expects data with a 'search_string' key.
    """
    check_tables()  # Call this function from your main if applicable
    data = request.json
    search_string = data.get('search_string')
    print(search_string)
    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400
    results = search_all_tables(search_string)
    #print(results)
    print(type(results))
    return results, 200#jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)
