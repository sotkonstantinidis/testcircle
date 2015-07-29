$(document).foundation({
  equalizer : {
    equalize_on_stack: true
  },
  interchange: {
    named_queries : {
      smallretina : 'only screen and (min-width: 1px) and (-webkit-min-device-pixel-ratio: 2), only screen and (min-width: 1px) and (min--moz-device-pixel-ratio: 2), only screen and (min-width: 1px) and (-o-min-device-pixel-ratio: 2/1), only screen and (min-width: 1px) and (min-device-pixel-ratio: 2), only screen and (min-width: 1px) and (min-resolution: 192dpi), only screen and (min-width: 1px) and (min-resolution: 2dppx)',
      mediumretina : 'only screen and (min-width: 641px) and (-webkit-min-device-pixel-ratio: 2), only screen and (min-width: 641px) and (min--moz-device-pixel-ratio: 2), only screen and (min-width: 641px) and (-o-min-device-pixel-ratio: 2/1), only screen and (min-width: 641px) and (min-device-pixel-ratio: 2), only screen and (min-width: 641px) and (min-resolution: 192dpi), only screen and (min-width: 641px) and (min-resolution: 2dppx)',
      largeretina : 'only screen and (min-width: 1025px) and (-webkit-min-device-pixel-ratio: 2), only screen and (min-width: 1025px) and (min--moz-device-pixel-ratio: 2), only screen and (min-width: 1025px) and (-o-min-device-pixel-ratio: 2/1), only screen and (min-width: 1025px) and (min-device-pixel-ratio: 2), only screen and (min-width: 1025px) and (min-resolution: 192dpi), only screen and (min-width: 1025px) and (min-resolution: 2dppx)'
    }
  }
});


var sourceSwap = function () {
  var $this = $(this);
  var newSource = $this.data('alt-src');
  $this.data('alt-src', $this.attr('src'));
  $this.attr('src', newSource);
}

// Replace svg with png if no svg
if (!Modernizr.svg) {
  $('img[src$=".svg"]').each(function() {
      //E.g replaces 'logo.svg' with 'logo.png'.
      $(this).attr('src', $(this).attr('src').replace('.svg', '.png'));
  });
}


/**
 * Updates elements of a form fieldset. Fields of a Django formset are
 * named "[prefix]-[index]-[fieldname]" and their ID is
 * "id_[prefix]-[index]-[fieldname]". When adding or removing elements
 * of a fieldset, the name and index need to be updated.
 *
 * This function udates the name and id of each input field inside the
 * given fieldset element. It also updates the "label-for" attribute for
 * any label found inside the given element.
 *
 * Use this function to correctly label newly added fields of a
 * questiongroup ("Add more") or to re-label the remaining fields after
 * removing a field from a questiongroup ("Remove").
 *
 * @param {Element} element - The form element.
 * @param {string} prefix - The prefix of the questiongroup.
 * @param {integer} index - The index of the element.
 * @param {boolean} reset - Whether to reset the values of the input
 * fields or not. Defaults to false (do not reset the values).
 */
function updateFieldsetElement(element, prefix, index, reset) {
  reset = (typeof reset === "undefined") ? false : true;
  var id_regex = new RegExp('(' + prefix + '-\\d+-)');
  var replacement = prefix + '-' + index + '-';
  element.find(':input').each(function() {
      var name = $(this).attr('name').replace(id_regex, replacement);
      var id = 'id_' + name;
      $(this).attr({'name': name, 'id': id});
      if (reset) {
        $(this).val('').removeAttr('checked');
      }
    });
    element.find('label').each(function() {
        var newFor = $(this).attr('for').replace(id_regex, replacement);
        $(this).attr('for', newFor);
    });
}

/**
 * Toggles CSS class "is-selected" for button bars. If a value is
 * selected, the row is highlighted. If no value (empty string or '') is
 * selected, it is not.
 *
 * $(this): div.button-bar
 */
function toggleButtonBarSelected() {
  var selectedValue = $(this).find('input[type="radio"]:checked').val();
  var item = $(this).closest('.list-item');
  if(selectedValue != 'none' && selectedValue != '') {
    item.addClass('is-selected');
  } else {
    item.removeClass('is-selected');
  }
  // item.toggleClass('is-selected', !(!selectedValue || 0 === selectedValue.length));
}

/**
 * Toggle the conditional image checkboxes if the parent checkbox was
 * clicked. If deselected, all conditional checkboxes are unchecked.
 *
 * el: div of conditional image checkboxes
 */
function toggleImageCheckboxConditional(el) {
  var topCb = el.parent('.list-gallery-item').find('input[data-toggle]');
  if (!topCb.is(':checked')) {
    el.find('input').removeAttr('checked')
  }
}


/**
 * Update the numbering of the questiongroups.
 */
function updateNumbering() {
  $('.questiongroup-numbered-inline').each(function() {
    var counter = 0;
    $(this).find('.row.list-item').each(function() {
      counter++;
      $(this).find('label').each(function() {
        var label = $(this).html();
        $(this).html(counter + ': ' + label);
      });
    });
  });
  $('.questiongroup-numbered-prefix').each(function() {
    var counter = 1;
    $(this).find('.questiongroup-numbered-number').each(function() {
      $(this).html(counter++ + ':');
    });
  });
}


$(function() {

  // Language switcher
  $('.top-bar-lang .dropdown a').click(function() {
    var lang = $(this).data('language');
    var form = $(this).closest('form');
    if (form && lang) {
      form.find('#language_field').val(lang);
      form.submit();
    }
  });

  $('#submit-search').click(function() {
    $(this).closest('form').submit();
    return false;
  });

  // Context switcher (WOCAT vs. Approaches vs. Technologies)
  $('.search-switch.button-switch input').click(function() {
    window.location = $(this).data('url');
  });

  $('img[data-alt-src]').each(function() {
      new Image().src = $(this).data('alt-src');
  }).hover(sourceSwap, sourceSwap);


  // UTILITIES
  // -----------------
  // Toggle view
  $('body').on('click', '[data-toggle]', function (e) {
    var target = $('#'+ $(this).data('toggle'));
    if($(this).parent().hasClass('list-gallery-item')){
      target.slideToggle();
      toggleImageCheckboxConditional(target);
    } else if($(this).parent().hasClass('button-bar')){
      var selectedValue = $(this).find('input[type="radio"]:checked').val();
      var item = $(this).closest('.list-item');
      if(selectedValue != 'none' && !item.hasClass('is-selected')) {
        target.slideToggle();
      }
      if(selectedValue === 'none' && item.hasClass('is-selected')) {
        target.slideToggle();
      }
    } else {
      e.preventDefault();
      target.slideToggle();

      // We have to refresh sliders if their are in a collapsed element (grip position issue)
      try {
        $('.nstSlider').nstSlider('refresh');
      } catch(e) {}
    }

  })

  // LIST ITEM
  // -----------------
  // List item remove
  .on('click', '.list-item-action[data-remove-this]', function (e) {

    var qg = $(this).closest('.list-item').data('questiongroup-keyword');
    var currentCount = parseInt($('#id_' + qg + '-TOTAL_FORMS').val());
    var maxCount = parseInt($('#id_' + qg + '-MAX_NUM_FORMS').val());
    var minCount = parseInt($('#id_' + qg + '-MIN_NUM_FORMS').val());

    var item = $(this).closest('.list-item.is-removable');
    item.remove();
    var otherItems = $('.list-item[data-questiongroup-keyword="' + qg + '"]');
    if (otherItems.length <= minCount) {
      otherItems.find('[data-remove-this]').hide();
    }
    otherItems.each(function(i, el) {
      updateFieldsetElement($(el), qg, i);
    });

    currentCount--;
    $('#id_' + qg + '-TOTAL_FORMS').val(currentCount);
    $('.list-action [data-add-item][data-questiongroup-keyword="' + qg + '"]').toggle(currentCount < maxCount);

    watchFormProgress();

  })
  // List item add
  .on('click', '.list-action [data-add-item]', function (e) {

    var qg = $(this).data('questiongroup-keyword');
    var currentCount = parseInt($('#id_' + qg + '-TOTAL_FORMS').val());
    var maxCount = parseInt($('#id_' + qg + '-MAX_NUM_FORMS').val());

    if (currentCount >= maxCount) return;

    var container = $(this).closest('.list-action');

    var otherItems = $('.list-item[data-questiongroup-keyword="' + qg + '"]');
    otherItems.find('[data-remove-this]').show();

    var lastItem = container.prev('.list-item');
    newElement = lastItem.clone();

    updateFieldsetElement(newElement, qg, currentCount, true);
    newElement.insertBefore(container);

    currentCount++;
    $('#id_' + qg + '-TOTAL_FORMS').val(currentCount);
    $(this).toggle(currentCount < maxCount);
  })

  // BUTTON BAR
  // -----------------
  // Button bar select line
  .on('click', '.button-bar', toggleButtonBarSelected);

  // Slider
  // -----------------
  // See full doc here: http://lokku.github.io/jquery-nstslider/
  try {
    $('.nstSlider').nstSlider({
      "crossable_handles": false,
      "left_grip_selector": ".leftGrip",
      "right_grip_selector": ".rightGrip",
      "value_bar_selector": ".bar",
      "value_changed_callback": function(cause, leftValue, rightValue, prevLeft, prevRight) {
        var $grip = $(this).find('.leftGrip'),
            whichGrip = 'left grip';
        if (leftValue === prevLeft) {
            $grip = $(this).find('.rightGrip');
            whichGrip = 'right grip';
        }
        var text = [];
        text.push('<b>Moving ' + whichGrip + '</b>');
        text.push('role: ' + $grip.attr('role'));
        text.push('aria-valuemin: ' + $grip.attr('aria-valuemin'));
        text.push('aria-valuenow: ' + $grip.attr('aria-valuenow'));
        text.push('aria-valuemax: ' + $grip.attr('aria-valuemax'));
        text.push('aria-disabled: ' + $grip.attr('aria-disabled'));
        $('.ariaAttributesAsText').html(text.join('<br />'));
        $(this).parent().find('.leftLabel').text(leftValue);
        $(this).parent().find('.rightLabel').text(rightValue);
      }
    });
  } catch(e) {}

  // Update the numbering of the questiongroups
  updateNumbering();
});

/**
 * Helper function to retrieve a Cookie in JavaScript. This is used for
 * example for form submission through AJAX to get the CSRF token needed
 * by Django to process the form.
 *
 * @param {string} name - The name of the cookie.
 * @return {string or null} The value of the cookie or "null" if no
 * cookie with the given name was found.
 */
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
