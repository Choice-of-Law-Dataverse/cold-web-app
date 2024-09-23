from config import Config
from services.search import SearchService
import utils.data_visualization

def main(data):
    # Simulating the search string input (normally received via request.json)
    search_string = data.get("search_string", "party autonomy switzerland")

    if not search_string:
        return {'error': 'No search string provided'}, 400

    # Assuming 'search_service' is instantiated somewhere
    search_service = SearchService()  # Create or mock the search service instance

    # Simulating the call to the search function
    results = search_service.curated_search(search_string)

    return results  # No need for jsonify as we're not using Flask

if __name__ == "__main__":
    # Simulating a sample request payload (normally obtained from request.json)
    sample_data = {
        "search_string": "party autonomy switzerland"
    }
    
    # Call main with sample data
    result = main(sample_data)
    
    utils.data_visualization.visualize_dict(result)