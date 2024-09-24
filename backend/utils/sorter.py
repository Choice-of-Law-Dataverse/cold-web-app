class Sorter:
    def __init__(self):
        pass

    def sort_by_similarity(self, results):
        return sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)

    def sort_by_completeness(self, data):
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

    def sort_by_case_rank(self, data):
        # Extract the court decision results
        court_decisions = data.get("tables", {}).get("Court decisions", {}).get("results", {})

        # Convert the nested dictionary to a list of tuples (ID, case_data) for easier sorting
        court_decisions_list = [(key, court_decisions[key]) for key in court_decisions]
        print(type(court_decisions_list))
        #print("Sample court decision:", court_decisions_list[:1])  # Print the first item for debugging

        # Define a function to retrieve the case rank, handling cases where it doesn't exist
        def get_case_rank(case):
            # Retrieve the "Case rank" value or assign infinity if it doesn't exist
            if "Case rank" in case[1]:
                #print(case[1]["ID"], "has the case rank of: ", case[1]["Case rank"])
                case_rank = int(case[1]["Case rank"])
            else:
                #print(case[0], "has no case rank")
                case_rank = float('-inf')

            #print(f"Case rank for case {case[0]}: {case_rank}")  # Print the case rank for debugging
            
            # Return the case rank if it's a valid number, otherwise return a large number for infinity
            return case_rank if isinstance(case_rank, (int, float)) else float('-inf')

        # Sort the list of court decisions by case rank (ascending)
        sorted_court_decisions = sorted(court_decisions_list, key=get_case_rank, reverse=True)
        #for i in range(len(sorted_court_decisions)):
            #print("Sorted court decision index number:", sorted_court_decisions[i][1]["ID"])
        
        # Rebuild the sorted dictionary
        sorted_results = {str(i): case_data for i, (key, case_data) in enumerate(sorted_court_decisions)}
        
        # Place the sorted results back into the original data structure
        data["tables"]["Court decisions"]["results"] = sorted_results
        
        return data

    def sorting_chain(self, data):
        data = self.sort_by_case_rank(data)
        data = self.sort_by_completeness(data)
        return data