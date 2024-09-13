from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from config import Config
from services.search import SearchService
from services.query_logging import log_query

# Create Flask app
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
CORS(app)

search_service = SearchService()

@app.route('/search', methods=['POST'])
def handle_search():
    data = request.json
    search_string = data.get('search_string')
    print(search_string)
    filter_string = data.get('filter_string')
    print(filter_string)
    use_semantic_search = data.get('use_semantic_search', False)

    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400

    if use_semantic_search:
        results = search_service.semantic_search(search_string)
    else:
        if filter_string:
            results = search_service.filtered_search(search_string, filter_string)
        else:
            results = search_service.basic_search(search_string)

    log_query(request, search_string, len(results))
    return jsonify(results), 200

@app.route('/curated_search', methods=['POST'])
def handle_curated_search():
    data = request.json
    search_string = data.get('search_string')
    print(search_string)

    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400

    results = search_service.curated_search(search_string)

    log_query(request, search_string, len(results))
    return jsonify(results), 200

@app.route('/curated_search/details', methods=['POST'])
def handle_curated_details_search():
    data = request.json
    table = data.get('table')
    print(table)
    if not table:
        return jsonify({'error': 'No table provided'}), 400
    id = data.get('id')
    print(id)
    if not id:
        return jsonify({'error': 'No id provided'}), 400

    results = search_service.curated_details_search(table, id)

    log_query(request, f"Details search in {table} for ID {id}", len(results))
    return jsonify(results), 200

# Retrieve information about the user
@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    # Set the Accept-CH header to request client hints
    response = jsonify({'message': 'Send Client Hints'})
    response.headers.set('Accept-CH', 'Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA, Sec-CH-UA-Mobile')
    return response

@app.route('/user_info', methods=['GET'])
def user_info():
    # Read the Client Hints from the headers
    brand = request.headers.get('Sec-CH-UA', 'Unknown')
    mobile = request.headers.get('Sec-CH-UA-Mobile', 'Unknown')
    platform = request.headers.get('Sec-CH-UA-Platform', 'Unknown Platform')
    platform_version = request.headers.get('Sec-CH-UA-Platform-Version', 'Unknown Version')
    model = request.headers.get('Sec-CH-UA-Model', 'Unknown Model')

    # Return the collected information
    return jsonify({
        'brand': brand,
        'mobile': mobile,
        'platform': platform,
        'platform_version': platform_version,
        'model': model
    })

if __name__ == "__main__":
    app.run(debug=True)
