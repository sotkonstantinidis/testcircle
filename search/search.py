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
