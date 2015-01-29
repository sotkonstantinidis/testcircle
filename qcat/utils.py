def find_dict_in_list(list_, key, value, not_found={}):
    """
    A helper function to find a dict based on a given key and value pair
    inside a list of dicts. Only the first occurence is returned if
    there are multiple dicts with the key and value.

    Args:
        ``list_`` (list): A list of dicts to search in.

        ``key`` (str): The key of the dict to look at.

        ``value`` (str): The value of the key the dict has to match.

    Kwargs:
        ``not_found`` (): The return value if no dict was found.
        Defaults to ``{}``.
    """
    if value is not None:
        for el in list_:
            if el.get(key) == value:
                return el
    return not_found
