class Sorter:
    def __init__(self):
        pass

    def sort_by_similarity(self, results):
        return sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)

    # New function for sorting search results based on "Case rank" and completeness
    def sort_by_priority_and_completeness(results):
        def completeness_score(entry):
            """Count the number of non-empty fields to determine completeness."""
            return sum(1 for value in entry.values() if value not in (None, '', [], {}))

        print(completeness_score(results))

        def sort_key(entry):
            #Priority sorting by 'Case rank' first and then by completeness.
            case_rank = entry.get('Case rank', None)
            table_name = entry.get('table', '')

            # Priority sorting by 'Case rank' for 'Court decisions' table
            if table_name == 'Court decisions':
                # Entries with missing 'Case rank' should be sorted to the bottom
                if case_rank is None or case_rank == '':
                    return (1, 0)  # Missing rank goes last, 0 completeness score
                return (0, -int(case_rank), completeness_score(entry))
            
            # For other entries, just sort by completeness
            return (1, completeness_score(entry))

        # Sort based on the computed key
        return sorted(results, key=sort_key)
        #return results

    def sort_by_key_value_pairs(self, data):
        # Access the 'Answers' and 'Court decisions' results
        answers_results = data['tables']['Answers']['results']
        court_results = data['tables']['Court decisions']['results']

        # Define a helper function to count key-value pairs
        def count_key_value_pairs(entry):
            return len(entry)

        # Sort 'Answers' based on the number of key-value pairs
        sorted_answers = dict(sorted(answers_results.items(), 
                                    key=lambda x: count_key_value_pairs(x[1]), 
                                    reverse=True))
        
        # Sort 'Court decisions' based on the number of key-value pairs
        sorted_court_decisions = dict(sorted(court_results.items(), 
                                            key=lambda x: count_key_value_pairs(x[1]), 
                                            reverse=True))
        
        # Return the sorted data, maintaining the original structure
        return {
            "tables": {
                "Answers": {
                    "matches": data['tables']['Answers']['matches'],
                    "results": sorted_answers
                },
                "Court decisions": {
                    "matches": data['tables']['Court decisions']['matches'],
                    "results": sorted_court_decisions
                }
            }
        }