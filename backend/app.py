import os
from flask import Flask, request, render_template
from markupsafe import escape, Markup
from datetime import datetime
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import re

app = Flask(__name__)

# get environment variables
load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
POSTGRES_AZURE_DBNAME = os.getenv("POSTGRES_AZURE_DBNAME")
POSTGRES_AZURE_HOST = os.getenv("POSTGRES_AZURE_HOST")
POSTGRES_AZURE_USER = os.getenv("POSTGRES_AZURE_USER")
POSTGRES_AZURE_PASSWORD = os.getenv("POSTGRES_AZURE_PASSWORD")

# DB Connection parameters for further use
dbname = POSTGRES_AZURE_DBNAME
user = POSTGRES_AZURE_USER
password = POSTGRES_AZURE_PASSWORD
host = POSTGRES_AZURE_HOST

def highlight_search_terms_with_context(value, search_terms, max_length=1000):
    """Highlights all search terms within the value, showing an optimal context around them."""
    # Escape the entire text first to ensure HTML safety
    escaped_value = escape(value)

    # Define a function to wrap matched terms with <mark> without escaping them again
    def highlight_match(match):
        return Markup(f"<mark>{match.group(0)}</mark>")

    # For each search term, apply highlighting using a regular expression for case-insensitive matching
    for term in search_terms:
        # Prepare the term for regex search (escape regex special characters)
        regex_term = re.escape(term)
        # Replace occurrences of the term with highlighted version
        escaped_value = re.sub(regex_term, highlight_match, escaped_value, flags=re.IGNORECASE)

    # Determine the optimal context to display based on the original (non-escaped) value's length
    # This is a simplified approach; you may need to adjust it to ensure the context is meaningful
    if len(value) > max_length:
        start = max(0, escaped_value.find("<mark>") - 30)  # Example: Start 30 chars before first highlight
        end = min(len(escaped_value), start + max_length)
        display_context = escaped_value[start:end]
        if start > 0:
            display_context = "..." + display_context
        if end < len(escaped_value):
            display_context += "..."
    else:
        display_context = escaped_value

    return Markup(display_context)

def generate_contexts_for_terms(value, search_terms, context_length=50):
    """Generates highlighted contexts for each occurrence of each search term."""
    escaped_value = escape(value)  # Escape the entire value for HTML safety
    
    def highlight_and_extract_context(match):
        # Calculate context bounds
        start = max(match.start() - context_length, 0)
        end = min(match.end() + context_length, len(escaped_value))
        
        # Extract context with highlighting
        context = escaped_value[start:match.start()] + Markup(f"<mark>{escaped_value[match.start():match.end()]}</mark>") + escaped_value[match.end():end]
        
        # Add ellipses if context is cut
        if start > 0:
            context = Markup("...") + context
        if end < len(escaped_value):
            context += Markup("...")
        return context

    contexts = []
    for term in search_terms:
        regex_term = re.escape(term)  # Prepare the term for regex search
        # Find all occurrences of the term and extract context for each
        term_contexts = [highlight_and_extract_context(match) for match in re.finditer(regex_term, escaped_value, flags=re.IGNORECASE)]
        contexts.extend(term_contexts)
    
    return contexts

def display_search_results_with_contexts(value, search_terms, context_length=50):
    """Displays separate contexts for each search term."""
    contexts = generate_contexts_for_terms(value, search_terms, context_length)
    if not contexts:
        return escape(value[:context_length]) + ("..." if len(value) > context_length else "")
    return Markup("<br><br>").join(contexts)  # Join different contexts with line breaks for display

def search_all_tables(search_string):
    results = ""
    total_matches = 0  # Initialize a counter for the total number of matches

    search_terms = search_string.split()
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, sslmode="require")
    cur = conn.cursor()

    try:
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        tables = cur.fetchall()

        for table in tables:
            table_name = table[0]
            cur.execute(sql.SQL("""SELECT column_name FROM information_schema.columns 
                                    WHERE table_name = %s AND table_schema = 'public'"""), (table_name,))
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
            
            cur.execute(query, params)
            rows = cur.fetchall()

            if rows:
                total_matches += len(rows)  # Increment the total_matches by the number of matches found
                results += f"<div><strong>{len(rows)} matches found in table '{escape(table_name)}':</strong></div><br>"
                for i, row in enumerate(rows, start=1):
                    results += f"<div>Result {i}:<br><br>"
                    for idx, col in enumerate(cur.description):
                        colname = escape(col[0])
                        raw_value = str(row[idx])
                        display_value = display_search_results_with_contexts(raw_value, search_terms, 100)
                        results += f"<div><small>{colname}</small><br>{display_value}</div><br>"
                    results += "<div><hr></div><br>"
                
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

    # Include the total count of matches at the beginning or end of the results
    total_results_summary = f"<div>Total matches found across all tables: <strong>{total_matches}</strong></div><br>"
    return total_results_summary + f"<div><hr></div>" + results  # Adjust based on whether you want the summary at the beginning or end

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_string = request.form['search_string']

        # Record the search query with a timestamp
        with open("search_queries.log", "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{timestamp} - {search_string}\n")

        # Call the search function
        search_output = search_all_tables(search_string)
        
        # Pass the entire output as a single variable to the template
        return render_template('index.html', search_string=search_string, search_output=search_output)
    else:
        # Handle the GET request
        return render_template('index.html', search_string="", search_output="")

if __name__ == "__main__":
    default_port = 5000
    port = int(os.getenv('PORT', default_port))
    app.run(host='0.0.0.0', port=port)