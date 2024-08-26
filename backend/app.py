from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from config import Config
from services.search import SearchService

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

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)
