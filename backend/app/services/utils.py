import logging
import re

logger = logging.getLogger(__name__)

"""
=======================DATA HANDLING===========================
"""


def list_to_dict(lst):
    return dict(enumerate(lst))


def parse_results(obj):
    if isinstance(obj, dict):
        transformed = {}
        for key, value in obj.items():
            transformed[key] = parse_results(value)
        return transformed
    elif isinstance(obj, list):
        return [parse_results(item) for item in obj]
    else:
        # not a dict or list, just return as-is
        return obj


def filter_na(obj):
    if isinstance(obj, dict):
        filtered = {}
        for key, value in obj.items():
            val_filtered = filter_na(value)  # recurse
            if val_filtered not in (None, "", [], {}):
                filtered[key] = val_filtered
        return filtered
    elif isinstance(obj, list):
        new_list = []
        for item in obj:
            val_filtered = filter_na(item)
            # Only keep non-empty items
            if val_filtered not in (None, "", [], {}):
                new_list.append(val_filtered)
        return new_list
    else:
        return obj


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
                    items.extend(flatten_json({f"{new_key}{sep}{i}": item}, "", sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    for table_name, table_data in data["tables"].items():
        for _result_key, result_data in table_data["results"].items():
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
                    logger.debug("Problematic subdictionary found under key '%s':", key.strip())
                    logger.debug(subdict)
                    logger.debug("Problematic characters:")
                    for char in problematic_chars:
                        logger.debug("Character: '%s' (Unicode: U+%04X)", char, ord(char))
                    logger.debug("=" * 50)
                    problematic_dicts.append(subdict)
                    break

    check_and_collect(data)
    return problematic_dicts


def deduplicate_entries(entries):
    """
    Remove duplicate entries from a list where duplicates have the same 'id' and 'source_table'.

    Parameters:
        entries (list): A list of dictionaries. Each dictionary should have 'id' and 'source_table' keys.

    Returns:
        list: A deduplicated list of entries.
    """
    seen = set()
    deduped_entries = []
    for entry in entries:
        key = (entry.get("id"), entry.get("source_table"))
        if key not in seen:
            seen.add(key)
            deduped_entries.append(entry)
    return deduped_entries
