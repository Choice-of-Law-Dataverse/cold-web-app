def list_to_dict(lst):
    return {i: item for i, item in enumerate(lst)}

def parse_results(nested_dict):
    transformed_dict = {}
    for key, value in nested_dict.items():
        if isinstance(value, list):
            value = list_to_dict(value)
        if isinstance(value, dict):
            value = parse_results(value)
        transformed_dict[key] = value
    return transformed_dict

def filter_na(nested_dict):
    filtered_dict = {}
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            value = filter_na(value)
        if value not in (None, '', [], {}):
            filtered_dict[key] = value
    return filtered_dict

def flatten_and_transform_data(data):
    flattened_data = []

    def flatten_json(json_object, parent_key='', sep='_'):
        items = []
        for k, v in json_object.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(flatten_json({f"{new_key}{sep}{i}": item}, '', sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    for table_name, table_data in data['tables'].items():
        for result_key, result_data in table_data['results'].items():
            flattened_result = flatten_json(result_data)
            flattened_result['table'] = table_name
            flattened_data.append(flattened_result)
    
    return flattened_data

def sort_by_similarity(results):
    return sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)


# New function for sorting search results based on "Case rank" and completeness
def sort_by_priority_and_completeness(results):
    def completeness_score(entry):
        """Count the number of non-empty fields to determine completeness."""
        return sum(1 for value in entry.values() if value not in (None, '', [], {}))

    def sort_key(entry):
        """Priority sorting by 'Case rank' first and then by completeness."""
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