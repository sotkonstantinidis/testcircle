$(function () {

    // Button to remove a filter. As the filter buttons are added
    // dynamically, the event needs to be attached to an element which is
    // already there.
    $('body').on('click', 'a.remove-filter', function () {
        var $t = $(this);

        var p = removeFilter($t.data('questiongroup'), $t.data('key'), $t.data('value'));

        // Always delete the paging parameter if the filter was modified
        delete p['page'];

        var s = ['?', $.param(p, traditional = true)].join('');
        changeUrl(s);
        updateList(s);

        return false;
    })

    // Button to reset all filters
    .on('click', '#filter-reset', function () {

        var p = parseQueryString();

        // Remove all filter parameters
        p = removeFilterParams(p);

        // Always delete the paging parameter if the filter was modified
        delete p['page'];

        // For advanced filtering, never remove the "type" filter (respectively
        // add it again)
        if ($(this).closest('form').hasClass('filter-advanced')) {
            p = addFilter(p, {key: 'type'}, getConfigurationType());

            // Also remove any advanced filter. But do not remove the template!
            $('.js-filter-item').not('#filter-additional-template .js-filter-item').remove();
        }

        var s = ['?', $.param(p, traditional = true)].join('');
        changeUrl(s);
        updateList(s);
        return false;
    })

    .on('change', '#search-advanced input[data-toggle-sub]', function() {
        // Show or hide sub filters.
        var checked = $(this).is(':checked');
        var subfilter = $('#' + $(this).data('toggle-sub'));
        if (!checked) {
            // If unselected, uncheck all sub filters
            subfilter.find('input').prop('checked', false)
        }
        subfilter.toggle(checked);
    });

    // Button to submit the filter
    $('#search-advanced').submit(function (e) {
        e.preventDefault();
        var queryString = createQueryString(getFilterQueryParams());
        changeUrl(queryString);
        updateList(queryString);
        return false;
    });

    $('body').on('click', '#pagination a', function () {
        var s = $(this).attr('href');
        changeUrl(s);
        updateList(s);
        return false;
    })

    // If a new filter item is added, use the template HTML to display it.
    .on('click', '#filter-add-new', function(e) {
        e.preventDefault();

        var template = $('#filter-additional-template');
        var row = $(this).closest('.row');
        $(template.html()).insertBefore(row);
    })

    // After a type (e.g. "technologies") was selected for the advanced filter,
    // redirect to the filter page by keeping all the currently active filters.
    .on('click', '.js-filter-advanced-type', function(e) {
        e.preventDefault();
        
        var type_ = $(this).data('type');
        var filterUrl = $(this).closest('div').data('filter-url');

        // Get the currently active filter parameters
        var p = getFilterQueryParams();

        // Manually set "type"
        p['type'] = [type_];

        // Redirect to filter URL
        window.location = filterUrl + createQueryString(p);
    })

    // When removing a filter, submit the form again after the filter item was
    // removed.
    .on('click', '.js-filter-remove', function(e) {
        e.preventDefault();
        var filter = $(this).closest('.row');
        var form = $(this).closest('form');
        filter.remove();
        form.submit();
    })

    // When selecting a key, query the available values for this key.
    .on('change', '.filter-key-select', function() {

        var filter = $(this).closest('.row');
        var valueColumn = filter.find('.filter-value-column');

        var url = $('#filter-add-new').data('value-url');

        // Add filter parameters to URL
        var filterParams = getFilterQueryParams();
        filterParams['key_path'] = [this.value];

        $.get(url + createQueryString(filterParams), function(data) {
            valueColumn.html(data);

            // If there is an initial questiongroup, check the initial values.
            if (filter.attr('data-initial-qg')) {
                var value = filter.data('initial-value');
                value.split(',').forEach(function(v) {
                    filter.find('input:checkbox[value=' + v + ']').attr('checked', true);
                });
            }
        });
    });

    // Slider
    // -----------------
    // See full doc here: http://lokku.github.io/jquery-nstslider/
    $('.nstSlider.filter-created').nstSlider({
        "crossable_handles": false,
        "left_grip_selector": ".leftGrip.filter-created",
        "right_grip_selector": ".rightGrip.filter-created",
        "value_bar_selector": ".bar.filter-created",
        "value_changed_callback": function (cause, leftValue, rightValue, prevLeft, prevRight) {
            $(this).parent().find('.leftLabel.filter-created').text(leftValue);
            $(this).parent().find('.rightLabel.filter-created').text(rightValue);
            $(this).parent().find('.min.filter-created').val(leftValue);
            $(this).parent().find('.max.filter-created').val(rightValue);
        }
    });
    $('.nstSlider.filter-updated').nstSlider({
        "crossable_handles": false,
        "left_grip_selector": ".leftGrip.filter-updated",
        "right_grip_selector": ".rightGrip.filter-updated",
        "value_bar_selector": ".bar.filter-updated",
        "value_changed_callback": function (cause, leftValue, rightValue, prevLeft, prevRight) {
            $(this).parent().find('.leftLabel.filter-updated').text(leftValue);
            $(this).parent().find('.rightLabel.filter-updated').text(rightValue);
            $(this).parent().find('.min.filter-updated').val(leftValue);
            $(this).parent().find('.max.filter-updated').val(rightValue);
        }
    });

    // Initiate chosen fields
    activateChosen();
});


/**
 * Activate the chosen fields of the filter.
 */
function activateChosen() {
    $('#search-advanced').find('.chosen-select').chosen({
      allow_single_deselect: true,
      search_contains: true
    });
}


/**
 * Helper method to return the currently selected SLM Data Type.
 *
 * @returns {*|jQuery}
 */
function getConfigurationType() {
    return $('#search-type').val();
}

/**
 * Create a query parameter object from the currently selected filters.
 *
 * @returns {*}
 */
function getFilterQueryParams() {
    var p = parseQueryString();

    // track search
    if (typeof _paq !== 'undefined') {
        _paq.push(['trackEvent', 'Filter', 'Value', p]);
    }

    // Remove all filter parameters
    p = removeFilterParams(p);

    // Always delete the paging parameter if the filter was modified
    delete p['page'];

    // Type (all, technologies, approaches)
    var type_ = getConfigurationType();
    if (type_) {
        p = addFilter(p, {key: 'type'}, type_);
    }

    var search_div = $('#search-advanced');

    // Radio
    search_div.find('input:radio').each(function() {
        var $t = $(this);
        if ($t.is(':checked')) {
            p = addFilter(p, {
                filter_parts: [$t.data('questiongroup'), $t.data('key')]
            }, $t.data('value'));
        }
    });

    // Checkboxes
    search_div.find('input:checkbox:checked').each(function() {
        var key_path = $(this).closest('div').data('key-path');
        p = addFilter(p, {filter_parts: [key_path]}, this.value);
    });

    // Search
    search_div.find('input[type=search]').each(function() {
        var $t = $(this);
        var val = $t.val();
        if (val) {
            p = addFilter(p, {key: 'q'}, val);
        }
    });

    // Sliders
    $('.nstSlider').each(function () {
        var qs = $(this).data('keyword');
        var min_val = $(this).parent().find('.min').val();
        var max_val = $(this).parent().find('.max').val();
        var min = $(this).data('cur_min');
        var max = $(this).data('cur_max');
        if (qs && min_val && max_val && !(min == min_val && max == max_val)) {
            p = addFilter(p, {key: qs}, [min_val, max_val].join('-'));
        }
    });

    // Text inputs, also hidden
    $('#search-advanced input[type=text], #search-advanced input[type=hidden]').each(function () {
        var $t = $(this);
        var qg = $t.data('questiongroup');
        var key = $t.data('key');
        var val = $t.val();
        if (qg && key && val) {
            p = addFilter(p, {filter_parts: [qg, key]}, val);
        }
    });
    // select
    search_div.find('select').each(function() {
        var qg = $(this).data('questiongroup');
        var key = $(this).data('key');
        var val = $(this).find('option:selected').val();
        if (qg && key && val) {
            p = addFilter(p, {filter_parts: [qg, key]}, val);
        }
    });

    return p;
}

/**
 * Join a query parameter object to form a query string.
 *
 * @param p
 * @returns {string}
 */
function createQueryString(p) {
    var query_parts = [];
    for (var key in p) {
        var values = p[key];
        query_parts.push([encodeURIComponent(key), values.map(encodeURIComponent).join('|')].join('='));
    }
    return '?' + query_parts.join('&');
}


/**
 * Add a filter to the query parameters.
 *
 * @param p: The object containing the query parameters.
 * @param key_options: An object containing either a "key" or "filter_parts"
 *  (list of questiongroup and key) which will be concatenated to form a filter.
 * @param value: String, the value.
 * @returns {*} Object containing query parameters. The values are always lists.
 */
function addFilter(p, key_options, value) {
    var key = key_options.key;
    if (!key) {
        // Concatenate filter parts
        key = createFilterParameter(key_options.filter_parts);
    }
    if (key in p) {
        p[key].push(value);
    } else {
        p[key] = [value];
    }
    return p;
}

/**
 * Concatenate parts of a filter (usually questiongroup and key) to form a
 * filter string.
 *
 * @param filter_parts
 * @returns {*|string|!Array.<T>}
 */
function createFilterParameter(filter_parts) {
    filter_parts.unshift('filter');
    return filter_parts.join('__');
}

/**
 * Remove a filter from the list of existing ones. Does nothing if the
 * filter does not exist.
 *
 * @param {string} questiongroup - The keyword of the questiongroup.
 * @param {string} key - The keyword of the key.
 * @param {string} value - The keyword of the value.
 * @return {object} An object with the updated query parameters.
 */
function removeFilter(questiongroup, key, value) {
    var keyParameter;
    if (key == '_search') {
        keyParameter = 'q';
        value = encodeURIComponent(value).replace('%20', '+');
    } else if (key == 'created' || key == 'updated' || key == 'flag') {
        keyParameter = key;
    } else if (key == 'funding_project_display') {
        key = key.replace('_display', '');
        keyParameter = keyParameter = createKeyParameter(questiongroup, key);
    } else {
        keyParameter = createKeyParameter(questiongroup, key);
    }
    var p = parseQueryString();
    if (keyParameter in p) {
        var i = p[keyParameter].indexOf(String(value));
        if (i > -1) {
            p[keyParameter].splice(i, 1);
        }
    }
    return p;
}

/**
 * Update the list based on the filter. Show a loading indicator and
 * send the filter through an AJAX request. If successful, update the
 * list and the active filters as well as the pagination. Hide the
 * loading indicator.
 *
 * @param {string} queryParam - The query parameter string to be
 * attached to the AJAX url.
 */
function updateList(queryParam) {
    var url = $('#search-advanced').data('url');
    if (typeof(url) == "undefined") {
        return;
    }

    $('.loading-indicator').show();
    $.ajax({
        url: [url, queryParam].join(''),
        type: 'GET',
        success: function (data) {
            $('#search-advanced').html(data.rendered_filter);
            $('#questionnaire-list').html(data.rendered_list);
            $('#questionnaire-count').html(data.count);
            $('#pagination').html(data.pagination);

            activateChosen();

            $('.loading-indicator').hide();
        },
        error: function (data) {
            // alert('Something went wrong');
            $('.loading-indicator').hide();
        }
    });
}

/**
 * Update the URL of the browser without refreshing the page. If the
 * browser does not support this HTML5 feature, do a redirect to the
 * given URL
 *
 * If the current URL is not yet the filter view, a redirect happens to
 * take the user to the filter view.
 *
 * @param {string} url - The new URL.
 */
function changeUrl(url) {
    var listUrl = $('#search-advanced').data('list-url');
    if (listUrl) {
        if (window.location.pathname.indexOf(listUrl) < 0) {
            // Redirect to list view if not there already
            window.location = listUrl + url;
            return;
        }
        if (typeof (history.pushState) != "undefined") {
            history.pushState(null, "", url);
        } else {
            window.location = url;
        }
    } else {
        window.location = url;
    }
}

/**
 * Delete all filter parameters from the query string.
 *
 * @param {object} p - The object containing the query parameters.
 * @return {object} The updated object with the query parameters.
 */
function removeFilterParams(p) {
    for (var k in p) {
        if (k.lastIndexOf('filter__', 0) === 0 || k == 'created' || k == 'updated' || k == 'flag' || k == 'type' || k == 'q') {
            delete p[k];
        }
    }
    return p;
}

/**
 * The reverse function of ``parseKeyParameter``.
 *
 * Helper function to create the string needed as query parameter for a
 * filter.
 *
 * The current format is:
 * filter__[questiongroup]__[key]
 *
 * Example:
 * filter__qg_11__key_14
 *
 * @param {string} questiongroup - The keyword of the questiongroup.
 * @param {string} key - The keyword of the key.
 * @return {string} The query parameter string.
 */
function createKeyParameter(questiongroup, key) {
    return ['filter', questiongroup, key].join('__');
}

/**
 * The reverse function of ``createKeyParameter``.
 *
 * Helper function to extract the questiongroup and key from the filter
 * parameter.
 *
 * @param {string} param - The filter parameter.
 * @return {array} An array containing the [0] questiongroup and [1] key
 * of the parameter. If not in the valid format, an empty array is
 * returned.
 */
function parseKeyParameter(param) {
    var parsed = param.split('__');
    if (parsed.length !== 3) return [];
    return [parsed[1], parsed[2]];
}

/**
 * Helper function to extract the query string from the URL. Can handle
 * repeating keys. Returns an object with values as arrays.
 * http://codereview.stackexchange.com/a/10396
 */
function parseQueryString() {
    var query = (location.search || '?').substr(1),
        map = {};
    query.replace(/([^&=]+)=?([^&]*)(?:&+|$)/g, function (match, key, value) {
        (map[key] = map[key] || []).push(value);
    });
    return map;
}
