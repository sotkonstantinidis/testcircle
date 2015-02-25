import math
from django import template

register = template.Library()


@register.filter
def columnize(items, columns):
    """
    Return a list containing lists of the elements which are contained
    in each column if the items are distributed evenly across the
    columns.

    If the division does not return integers, more items will be added
    for the first columns, lesser in the last. If there are more columns
    than items then empty lists will be added.

    Somewhat based on https://djangosnippets.org/snippets/2236/

    Examples::
        columnize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2)
        # [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]

        columnize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
        # [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]

    Usage in template::
        {% load list_to_columns %}

        {{ items|columnize:4 }}

    Args:
        ``items`` (list): A list of items to be distributed

        ``columns`` (int): Over how many columns the items are to be
        distributed.
    """
    len_items = len(items)
    el_columns = []
    el_index = 0
    for col in range(columns):
        col_size = int(math.ceil(float(len_items) / columns))
        el_columns.append(items[el_index:el_index+col_size])
        el_index += col_size
        len_items -= col_size
        columns -= 1
    return el_columns
