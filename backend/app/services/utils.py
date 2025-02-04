import re
import requests
from fastapi import Request
from app.config import config

"""
=======================DATA HANDLING===========================
"""

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
        if value not in (None, "", [], {}):
            filtered_dict[key] = value
    return filtered_dict


def flatten_and_transform_data(data):
    flattened_data = []

    def flatten_json(json_object, parent_key="", sep="_"):
        items = []
        for k, v in json_object.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(
                        flatten_json({f"{new_key}{sep}{i}": item}, "", sep=sep).items()
                    )
            else:
                items.append((new_key, v))
        return dict(items)

    for table_name, table_data in data["tables"].items():
        for result_key, result_data in table_data["results"].items():
            flattened_result = flatten_json(result_data)
            flattened_result["table"] = table_name
            flattened_data.append(flattened_result)

    return flattened_data


def find_problematic_subdict(data):
    problematic_dicts = []

    def check_and_collect(subdict):
        for key, value in subdict.items():
            if isinstance(value, dict):
                check_and_collect(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        check_and_collect(item)
            elif isinstance(value, str):
                # Find non-ASCII characters in the string value
                # problematic_chars = re.findall(r'[^\x00-\x7F]', value)
                # problematic_chars = re.findall(r'[^\x20-\x7E\xA0-\xFF]', value)
                problematic_chars = re.findall(r"[^\x00-\xFF]", value)
                # problematic_chars = re.findall(r'[\x00-\x08\x0E-\x1F\x7F-\x9F]', value)
                if problematic_chars:
                    print(f"Problematic subdictionary found under key '{key}':")
                    print(subdict)
                    print("Problematic characters:")
                    for char in problematic_chars:
                        print(f"Character: '{char}' (Unicode: U+{ord(char):04X})")
                    print("=" * 50)
                    problematic_dicts.append(subdict)
                    break

    check_and_collect(data)
    return problematic_dicts


"""
=========================QUERY LOGGING=======================
"""

# Utility function to get location from IP address using an external API
def get_location(ip_address: str):
    access_token = config.IPINFO_ACCESS_TOKEN
    try:
        response = requests.get(f"http://ipinfo.io/{ip_address}/json?token={access_token}")
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting location: {e}")
        return None
