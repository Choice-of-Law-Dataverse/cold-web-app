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