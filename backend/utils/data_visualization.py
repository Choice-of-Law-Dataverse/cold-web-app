from anytree import Node, RenderTree

def dict_to_tree(d, parent=None):
    for k, v in d.items():
        node = Node(k, parent=parent)
        if isinstance(v, dict):
            dict_to_tree(v, parent=node)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                sub_node = Node(f"{k}[{i}]", parent=node)
                if isinstance(item, dict):
                    dict_to_tree(item, parent=sub_node)
                else:
                    Node(trim_value(item), parent=sub_node)
        else:
            Node(trim_value(v), parent=node)

def trim_value(value):
    """
    Trims a string to a maximum of seven words.
    If the value is not a string, it is returned as is.
    """
    if isinstance(value, str):
        words = value.split()
        if len(words) > 7:
            return ' '.join(words[:7]) + '...'
        return value
    return value

def visualize_dict(data):
    """
    Converts a nested dictionary into a tree structure and prints it.
    
    :param data: The nested dictionary to visualize.
    """
    root = Node("root")
    dict_to_tree(data, root)
    for pre, _, node in RenderTree(root):
        print(f"{pre}{node.name}")
