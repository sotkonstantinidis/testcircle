import collections
from django.conf import settings
from elasticsearch import TransportError

from .index import get_elasticsearch
from .utils import get_alias


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
    return es.search(index=alias, q=get_escaped_string(query_string))


def get_es_query(
        filter_params: list=None, query_string: str='',
        match_all: bool=True) -> dict:
    """
    Kwargs:
        ``filter_params`` (list): A list of filter parameters. Each
        parameter is a tuple consisting of the following elements:

            [0]: questiongroup

            [1]: key

            [2]: values (list)

            [3]: operator

            [4]: type (eg. checkbox / text)

        ``query_string`` (str): A query string for the full text search.

        ``match_all`` (bool): Whether the query MUST match all filters or not.
        If not all filters must be matched, the results are ordered by relevance
        to show hits matching more filters at the top. Defaults to False.

    Returns:
        ``dict``. A dictionary containing the query to be passed to ES.
    """
    if filter_params is None:
        filter_params = []

    es_queries = []

    def _get_match(qg, k, v):
        return {
            'match': {
                f'data.{qg}.{k}': v
            }
        }

    # Filter parameters: Nested subqueries to access the correct
    # questiongroup.
    for filter_param in list(filter_params):

        if filter_param.type in [
                'checkbox', 'image_checkbox', 'select_type', 'select_model',
                'radio', 'bool']:

            # So far, range operators only works with one filter value. Does it
            # even make sense to have multiple of these joined by OR with the
            # same operator?
            if filter_param.operator in ['gt', 'gte', 'lt', 'lte']:
                query = {
                    'range': {
                        f'data.{filter_param.questiongroup}.'
                        f'{filter_param.key}_order': {
                            filter_param.operator: filter_param.values[0]
                        }
                    }
                }
            else:
                if len(filter_param.values) > 1:
                    matches = [
                        _get_match(filter_param.questiongroup,
                                          filter_param.key, v) for v in
                        filter_param.values]
                    query = {
                        'bool': {
                            'should': matches
                        }
                    }
                else:
                    query = _get_match(
                        filter_param.questiongroup, filter_param.key,
                        filter_param.values[0])

            es_queries.append({
                'nested': {
                    'path': f'data.{filter_param.questiongroup}',
                    'query': query
                }
            })

        elif filter_param.type in ['text', 'char']:
            es_queries.append({
                "nested": {
                    "path": "data.{}".format(filter_param.questiongroup),
                    "query": {
                        "multi_match": {
                            "query": filter_param.values[0],
                            "fields": ["data.{}.{}.*".format(
                                filter_param.questiongroup, filter_param.key)],
                            "type": "most_fields",
                        }
                    }
                }
            })

        elif filter_param.type in ['_date']:
            years = filter_param.values[0].split('-')
            if len(years) != 2:
                continue
            es_queries.append({
                'range': {
                    filter_param.key: {
                        'from': '{}||/y'.format(years[0]),
                        'to': '{}||/y'.format(years[1]),
                    }
                }
            })

        elif filter_param.type in ['_flag']:
            es_queries.append({
                'nested': {
                    'path': 'flags',
                    'query': {
                        'query_string': {
                            'query': filter_param.values[0],
                            'fields': ['flags.flag'],
                        }
                    }
                }
            })

        elif filter_param.type in ['_lang']:
            es_queries.append({
                'terms': {
                    'translations': [filter_param.values]
                }
            })

    if query_string:
        es_queries.append({
            "query_string": {
                "query": get_escaped_string(query_string)
            }
        })

    es_bool = 'must' if match_all is True else 'should'

    return {
        "query": {
            "bool": {
                es_bool: es_queries
            }
        },
        "sort": [
            {
                "data.qg_location.country": {
                    "order": "asc",
                    "nested_path": "data.qg_location"
                }
            },
            "_score",
        ]
    }


def advanced_search(
        filter_params: list=None, query_string: str='',
        configuration_codes: list=None, limit: int=10,
        offset: int=0, match_all: bool=True) -> dict:
    """
    Kwargs:
        ``filter_params`` (list): A list of filter parameters. Each
        parameter is a tuple consisting of the following elements:

            [0]: questiongroup

            [1]: key

            [2]: values (list)

            [3]: operator

            [4]: type (eg. checkbox / text)

        ``query_string`` (str): A query string for the full text search.

        ``configuration_codes`` (list): An optional list of
        configuration codes to limit the search to certain indices.

        ``limit`` (int): A limit of query results to return.

        ``offset`` (int): The number of query results to skip.

        ``match_all`` (bool): Whether the query MUST match all filters or not.
        If not all filters must be matched, the results are ordered by relevance
        to show hits matching more filters at the top. Defaults to False.

    Returns:
        ``dict``. The search results as returned by
        ``elasticsearch.Elasticsearch.search``.
    """
    query = get_es_query(
        filter_params=filter_params, query_string=query_string,
        match_all=match_all)

    alias = get_alias(configuration_codes)
    return es.search(index=alias, body=query, size=limit, from_=offset)


def get_aggregated_values(
        questiongroup, key, filter_params: list = None, query_string: str='',
        configuration_codes: list=None, match_all: bool=True) -> dict:

    if filter_params is None:
        filter_params = []

    # Remove the filter_param with the current questiongroup and key from the
    # list of filter_params
    relevant_filter_params = [
        f for f in filter_params if
        f.questiongroup != questiongroup and f.key != key]

    query = get_es_query(
        filter_params=relevant_filter_params, query_string=query_string,
        match_all=match_all)

    query.update({
        'aggs': {
            'qg': {
                'nested': {
                    'path': f'data.{questiongroup}'
                },
                'aggs': {
                    'values': {
                        'terms': {
                            'field': f'data.{questiongroup}.{key}',
                            # Include all aggregations, not only 10. Setting
                            # "size": 0 is deprecated, therefore setting a
                            # (hopefully) reasonably high limit manually.
                            # See https://github.com/elastic/elasticsearch/issues/18838
                            'size': 200,
                        }
                    }
                }
            }
        },
        'size': 0,  # Do not include the actual hits
    })

    alias = get_alias(configuration_codes)
    es_query = es.search(index=alias, body=query)

    buckets = es_query.get('aggregations', {}).get('qg', {}).get(
        'values', {}).get('buckets', [])

    return {b.get('key'): b.get('doc_count') for b in buckets}


def get_element(object_id: int, *configuration_codes) -> dict:
    """
    Get a single element from elasticsearch.
    """
    alias = get_alias(configuration_codes)
    try:
        return es.get_source(index=alias, id=object_id, doc_type='questionnaire')
    except TransportError:
        return {}


def get_escaped_string(query_string: str) -> str:
    """
    Replace all reserved characters when searching the ES index.
    """
    for char in settings.ES_QUERY_RESERVED_CHARS:
        query_string = query_string.replace(char, '\\{}'.format(char))
    return query_string


def get_indices_alias():
    """
    Return a list of all elasticsearch index aliases. Only ES indices which
    start with the QCAT prefix are respected.

    Returns:
        list.
    """
    indices = []
    for aliases in es.indices.get_alias('*').values():
        for alias in aliases.get('aliases', {}).keys():
            if settings.ES_INDEX_PREFIX not in alias:
                continue
            indices.append(alias.replace(settings.ES_INDEX_PREFIX, ''))
    return indices
