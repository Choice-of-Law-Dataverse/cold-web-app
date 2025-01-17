from config import Config
from services.search import SearchService
import utils.data_visualization
from utils.utils import find_problematic_subdict


def main(data):
    # Simulating the search string input (normally received via request.json)
    search_string = data.get("search_string", "party autonomy")

    if not search_string:
        return {"error": "No search string provided"}, 400

    # Assuming 'search_service' is instantiated somewhere
    search_service = SearchService()  # Create or mock the search service instance

    # Simulating the call to the search function
    # results = search_service.curated_search(search_string)
    results = search_service.full_text_search(search_string)

    return results  # No need for jsonify as we're not using Flask


def return_full_table():
    search_service = SearchService()
    results = search_service.full_table("Concepts")
    return results


if __name__ == "__main__":
    # Simulating a sample request payload (normally obtained from request.json)
    sample_data = {
        "search_string": "SIL Ceramiche SPA v Mezuraj ShPK [2013] High Court of Albania 11214-02700-00-2013"
    }

    # Call main with sample data
    result = main(sample_data)
    # result = return_full_table()
    find_problematic_subdict(result)

    # visualize_dict = utils.data_visualization.visualize_dict(result)

    # print(result)
