from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import logging
from config import Config
from services.search import SearchService
from services.query_logging import log_query
from services.ai import GPT

# Set up logging
logging.basicConfig(level=logging.DEBUG)
# Set PyMongo log level to WARNING to suppress DEBUG messages
logging.getLogger("pymongo").setLevel(logging.WARNING)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize Swagger
swagger = Swagger(app)

search_service = SearchService()
gpt = GPT()


@app.route("/full_text_search", methods=["POST"])
def handle_full_text_search():
    data = request.json
    search_string = data.get("search_string")
    filters = data.get("filters", [])
    print(filters)

    if not search_string:
        return jsonify({"error": "No search string provided"}), 400

    results = search_service.full_text_search(search_string, filters)
    log_query(
        request, search_string, filters, results["total_matches"], "full_text_search"
    )
    return jsonify(results), 200


@app.route("/curated_search/details", methods=["POST"])
def handle_curated_details_search():
    data = request.json
    table = data.get("table")
    if not table:
        return jsonify({"error": "No table provided"}), 400
    id = data.get("id")
    if not id:
        return jsonify({"error": "No id provided"}), 400

    results = search_service.curated_details_search(table, id)
    log_query(
        request,
        f"Details search in {table} for ID {id}",
        "NA",
        len(results),
        "curated_search/details",
    )
    return jsonify(results), 200


@app.route("/full_table", methods=["POST"])
def return_full_table():
    data = request.json
    table = data.get("table")
    filters = data.get("filters", [])

    if not table:
        return jsonify({"error": "No table provided"}), 400

    try:
        if filters:
            results = search_service.filtered_table(table, filters)
        else:
            results = search_service.full_table(table)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    log_query(
        request, f"Full table retrieval in {table}", filters, len(results), "full_table"
    )
    return jsonify(results), 200


@app.route("/get_user_info", methods=["GET"])
def get_user_info():
    response = jsonify({"message": "Send Client Hints"})
    response.headers.set(
        "Accept-CH",
        "Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA, Sec-CH-UA-Mobile",
    )
    return response


@app.route("/user_info", methods=["GET"])
def user_info():
    brand = request.headers.get("Sec-CH-UA", "Unknown")
    mobile = request.headers.get("Sec-CH-UA-Mobile", "Unknown")
    platform = request.headers.get("Sec-CH-UA-Platform", "Unknown Platform")
    platform_version = request.headers.get(
        "Sec-CH-UA-Platform-Version", "Unknown Version"
    )
    model = request.headers.get("Sec-CH-UA-Model", "Unknown Model")

    return jsonify(
        {
            "brand": brand,
            "mobile": mobile,
            "platform": platform,
            "platform_version": platform_version,
            "model": model,
        }
    )


@app.route("/classify_query", methods=["POST"])
def classify_query():
    data = request.json
    query = data.get("query")
    print(query)
    classification = gpt.classify_user_query(query)
    return classification


if __name__ == "__main__":
    app.run(debug=True)
