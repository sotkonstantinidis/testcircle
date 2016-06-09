from .index import get_elasticsearch
from .utils import (
    get_alias,
)


es = get_elasticsearch()


def simple_search(query_string, configuration_codes=[]):
    """
    Perform a simple full text search based on a query string.

    https://www.elastic.co/guide/en/elasticsearch/reference/1.6/search-search.html

    Args:
        ``query_string`` (str): The query string to be provided as ``q``
        parameter.

    Kwargs:
        ``configuration_codes`` (list): An optional list of
        configuration codes to limit the search to certain indices.

    Returns:
        ``dict``. The search results as returned by
        ``elasticsearch.Elasticsearch.search``.
    """
    alias = get_alias(configuration_codes)
    return es.search(index=alias, q=query_string)


def advanced_search(
        filter_params=[], query_string='', code='', name='',
        configuration_codes=[], limit=10, offset=0):
    """
    Kwargs:
        ``filter_params`` (list): A list of filter parameters. Each
        parameter is a tuple consisting of the following elements:

            [0]: questiongroup

            [1]: key

            [2]: value

            [3]: operator

            [4]: type (eg. checkbox / text)

        ``query_string`` (str): A query string for the full text search.

        ``code`` (str): The code of the questionnaire to search.

        ``name`` (str): The name of the questionnaire to search (search
        will happen in the ``name`` field of the questionnaire)

        ``configuration_codes`` (list): An optional list of
        configuration codes to limit the search to certain indices.

        ``limit`` (int): A limit of query results to return.

    Returns:
        ``dict``. The search results as returned by
        ``elasticsearch.Elasticsearch.search``.
    """
    alias = get_alias(configuration_codes)

    # TODO: Support more operator types.
    # TODO: Support AND/OR

    must = []

    # Filter parameters: Nested subqueries to access the correct
    # questiongroup.
    for filter_param in filter_params:
        questiongroup = filter_param[0]
        key = filter_param[1]
        value = filter_param[2]
        filter_type = filter_param[4]

        if filter_type in ['checkbox', 'image_checkbox', 'select_type']:
            must.append({
                "nested": {
                    "path": "data.{}".format(questiongroup),
                    "query": {
                        "query_string": {
                            "query": value,
                            "fields": ["data.{}.{}".format(questiongroup, key)]
                        }
                    }
                }
            })

        elif filter_type in ['text', 'char']:
            must.append({
                "nested": {
                    "path": "data.{}".format(questiongroup),
                    "query": {
                        "multi_match": {
                            "query": value,
                            "fields": ["data.{}.{}.*".format(
                                questiongroup, key)],
                            "type": "most_fields",
                        }
                    }
                }
            })

        elif filter_type in ['_date']:
            years = value.split('-')
            if len(years) != 2:
                continue
            must.append({
                'range': {
                    key: {
                        'from': '{}||/y'.format(years[0]),
                        'to': '{}||/y'.format(years[1]),
                    }
                }
            })

        elif filter_type in ['_flag']:
            must.append({
                'nested': {
                    'path': 'flags',
                    'query': {
                        'query_string': {
                            'query': value,
                            'fields': ['flags.flag'],
                        }
                    }
                }
            })

    # Query string: Full text search
    if query_string:
        must.append({
            "query_string": {
                "query": query_string
            }
        })

    should = []
    if code:
        should.append({
            'match': {
                'code': code,
            }
        })
    if name:
        should.append({
            'multi_match': {
                'query': name,
                'fields': ['name.*'],
                'type': 'most_fields',
            }
        })

    query = {
        "query": {
            "bool": {
                "must": must,
                'should': should,
            }
        },
        "sort": [
            {
                "updated": "desc"
            }
        ]
    }

    return es.search(index=alias, body=query, size=limit, from_=offset)
