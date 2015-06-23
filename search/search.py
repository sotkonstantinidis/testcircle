from .index import get_elasticsearch
from .utils import (
    get_alias,
)


es = get_elasticsearch()


def simple_search(query_string, configuration_code=None):
    """
    Perform a simple full text search based on a query string.

    https://www.elastic.co/guide/en/elasticsearch/reference/1.6/search-search.html

    Args:
        ``query_string`` (str): The query string to be provided as ``q``
        parameter.

    Kwargs:
        ``configuration_code`` (str): An optional coma-separated
        configuration_code to limit the search to certain indices.

    Returns:
        ``dict``. The search results as returned by
        ``elasticsearch.Elasticsearch.search``.
    """
    alias = None
    if configuration_code:
        alias = get_alias(configuration_code)
    return es.search(index=alias, q=query_string)


def advanced_search(search_arguments, configuration_code=None):
    """
    Args:
        ``search_arguments`` (list): A list of search arguments. Each
        argument is a tuple consisting of the following elements:

        [0]: questiongroup

        [1]: key

        [2]: value

        [3]: operator

    Kwargs:
        ``configuration_code`` (str): An optional coma-separated
        configuration_code to limit the search to certain indices.

    Returns:
        ``dict``. The search results as returned by
        ``elasticsearch.Elasticsearch.search``.
    """
    alias = None
    if configuration_code:
        alias = get_alias(configuration_code)

    # TODO: Support more operator types.

    nested_questiongroups = []
    for current_argument in search_arguments:
        questiongroup = current_argument[0]
        key = current_argument[1]
        value = current_argument[2]

        nested_questiongroups.append({
            "nested": {
                "path": "data.{}".format(questiongroup),
                "query": {
                    "multi_match": {
                        "query": value,
                        "fields": ["data.{}.{}.*".format(questiongroup, key)],
                        "type": "most_fields",
                    }
                }
            }
        })

    query = {
        "query": {
            "bool": {
                "must": nested_questiongroups
            }
        }
    }
    return es.search(index=alias, body=query)
