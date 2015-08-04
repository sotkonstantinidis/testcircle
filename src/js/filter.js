$(function() {

  // Button to remove a filter. As the filter buttons are added
  // dynamically, the event needs to be attached to an element which is
  // already there.
  $('body').on('click', 'a.remove-filter', function () {
    var $t = $(this),
        questiongroup = $t.data('questiongroup'),
        key = $t.data('key'),
        value = $t.data('value');

    var p = removeFilter(questiongroup, key, value);

    var s = ['?', $.param(p, traditional=true)].join('');
    changeUrl(s);
    updateFilter(s);
    return false;
  });

  // Button to reset all filters
  $('body').on('click', '#filter-reset', function() {
    var s = '?';
    changeUrl(s);
    updateFilter(s);
    return false;
  });

  // Button to submit the filter
  $('#submit-filter').click(function() {
    var p = {};

    // Checkboxes
    $('#search-advanced input:checkbox').each(function() {
      var $t = $(this);
      if ($t.is(':checked')) {
        p = addFilter($t.data('questiongroup'), $t.data('key'), $t.data('value'));
      }
    });

    var s = ['?', $.param(p, traditional=true)].join('');
    changeUrl(s);
    updateFilter(s);
    return false;
  });
});

/**
 * Add an additional filter to the existing ones.
 *
 * @param {string} questiongroup - The keyword of the questiongroup.
 * @param {string} key - The keyword of the key.
 * @param {string} value - The keyword of the value.
 * @return {object} An object with the updated query parameters.
 */
function addFilter(questiongroup, key, value) {
  var keyParameter = createKeyParameter(questiongroup, key);
  var p = parseQueryString();
  if (keyParameter in p) {
    p[keyParameter].push(value);
  } else {
    p[keyParameter] = [value];
  }
  return p;
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
  } else {
    keyParameter = createKeyParameter(questiongroup, key);
  }
  var p = parseQueryString();
  if (keyParameter in p) {
    var i = p[keyParameter].indexOf(value);
    if (i > -1) {
      p[keyParameter].splice(i, 1);
    }
  }
  return p;
}

/**
 * Update the filter. Show a loading indicator and send the filter
 * through an AJAX request. If successful, update the list and the
 * active filters. Hide the loading indicator.
 *
 * @param {string} filterString - The query filter string to be attached
 * to the AJAX url.
 */
function updateFilter(filterString) {

  var url = $('#search-advanced').data('url');
  if (typeof(url) == "undefined") {
    return;
  }

  $('.loading-indicator').show();
  $.ajax({
    url: [url, filterString].join(''),
    type: 'GET',
    success: function(data) {
      $('#questionnaire-list').html(data.list);
      $('#active-filters').html(data.active_filters);
      $('.loading-indicator').hide();
    },
    error: function(data) {
      alert('Something went wrong');
      $('.loading-indicator').hide();
    }
  });
}

/**
 * Update the URL of the browser without refreshing the page. If the
 * browser does not support this HTML5 feature, do a redirect to the
 * given URL
 *
 * @param {string} url - The new URL.
 */
function changeUrl(url) {
  if (typeof (history.pushState) != "undefined") {
    history.pushState(null,"", url);
  } else {
    window.location = url;
  }
}

/**
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
 * Helper function to extract the query string from the URL. Can handle
 * repeating keys. Returns an object with values as arrays.
 * http://codereview.stackexchange.com/a/10396
 */
function parseQueryString() {
      var query = (location.search || '?').substr(1),
          map   = {};
      query.replace(/([^&=]+)=?([^&]*)(?:&+|$)/g, function(match, key, value) {
          (map[key] = map[key] || []).push(value);
      });
      return map;
  }
