from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import logging
from config import Config
from services.search import SearchService
from services.query_logging import log_query

# Set up logging
logging.basicConfig(level=logging.DEBUG)
# Set PyMongo log level to WARNING to suppress DEBUG messages
logging.getLogger('pymongo').setLevel(logging.WARNING)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize Swagger
swagger = Swagger(app)

search_service = SearchService()

@app.route('/search', methods=['POST'])
def handle_search():
    """
    Search endpoint
    ---
    tags:
      - Search
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            search_string:
              type: string
            filter_string:
              type: string
            use_semantic_search:
              type: boolean
        description: The search parameters
    responses:
      200:
        description: Search results
        schema:
          type: array
          items:
            type: object
      400:
        description: Error message
    """
    data = request.json
    search_string = data.get('search_string')
    filter_string = data.get('filter_string')
    use_semantic_search = data.get('use_semantic_search', False)

    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400

    if use_semantic_search:
        results = search_service.semantic_search(search_string)
    else:
        results = search_service.filtered_search(search_string, filter_string) if filter_string else search_service.basic_search(search_string)

    log_query(request, search_string, len(results))
    return jsonify(results), 200

@app.route('/curated_search', methods=['POST'])
def handle_curated_search():
    """
    Curated search endpoint
    ---
    tags:
      - Curated Search
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            search_string:
              type: string
        description: Search using curated data
    responses:
      200:
        description: Curated search results
        schema:
          type: array
          items:
            type: object
      400:
        description: Error message
    """
    data = request.json
    search_string = data.get('search_string')

    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400

    results = search_service.curated_search(search_string)
    log_query(request, search_string, len(results))
    return jsonify(results), 200

@app.route('/curated_search/details', methods=['POST'])
def handle_curated_details_search():
    """
    Curated details search endpoint
    ---
    tags:
      - Curated Search
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            table:
              type: string
            id:
              type: string
        description: Search details within curated data
    responses:
      200:
        description: Details search results
        schema:
          type: object
      400:
        description: Error message
    """
    data = request.json
    table = data.get('table')
    if not table:
        return jsonify({'error': 'No table provided'}), 400
    id = data.get('id')
    if not id:
        return jsonify({'error': 'No id provided'}), 400

    results = search_service.curated_details_search(table, id)
    log_query(request, f"Details search in {table} for ID {id}", len(results))
    return jsonify(results), 200

@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    """
    Get user info
    ---
    tags:
      - User Info
    responses:
      200:
        description: Client user agent info
    """
    response = jsonify({'message': 'Send Client Hints'})
    response.headers.set('Accept-CH', 'Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA, Sec-CH-UA-Mobile')
    return response

@app.route('/user_info', methods=['GET'])
def user_info():
    """
    Return user info based on Client Hints
    ---
    tags:
      - User Info
    responses:
      200:
        description: Detailed user information
        schema:
          type: object
          properties:
            brand:
              type: string
            mobile:
              type: string
            platform:
              type: string
            platform_version:
              type: string
            model:
              type: string
    """
    brand = request.headers.get('Sec-CH-UA', 'Unknown')
    mobile = request.headers.get('Sec-CH-UA-Mobile', 'Unknown')
    platform = request.headers.get('Sec-CH-UA-Platform', 'Unknown Platform')
    platform_version = request.headers.get('Sec-CH-UA-Platform-Version', 'Unknown Version')
    model = request.headers.get('Sec-CH-UA-Model', 'Unknown Model')

    return jsonify({
        'brand': brand,
        'mobile': mobile,
        'platform': platform,
        'platform_version': platform_version,
        'model': model
    })

if __name__ == "__main__":
    app.run(debug=True)
