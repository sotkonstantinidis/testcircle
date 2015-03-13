$(document).foundation({
  equalizer : {
    equalize_on_stack: true
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
  item.toggleClass('is-selected', !(!selectedValue || 0 === selectedValue.length));
}

/**
 * Toggle the conditional image checkboxes if the parent checkbox was
 * clicked. If deselected, all conditional checkboxes are unchecked.
 *
 * el: div of conditional image checkboxes
 */
function toggleImageCheckboxConditional(el) {
  console.log(el);
  var topCb = el.parent('.list-gallery-item').find('input[data-toggle]');
  if (!topCb.is(':checked')) {
    el.find('input').removeAttr('checked')
  }
}

$(function() {
  $('img[data-alt-src]').each(function() {
      new Image().src = $(this).data('alt-src');
  }).hover(sourceSwap, sourceSwap);


  // UTILITIES
  // -----------------
  // Toggle view
  $('body').on('click', '.list-gallery-item [data-toggle]', function (e) {
    var target = $('#'+ $(this).data('toggle'));
    target.toggle();
    toggleImageCheckboxConditional(target);
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
    $('.list-action [data-add-item][data-questiongroup-keyword="' + qg + '"]').toggleClass('disabled', currentCount >= maxCount);

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
    $(this).toggleClass('disabled', currentCount >= maxCount);
  })

  // BUTTON BAR
  // -----------------
  // Button bar select line
  .on('click', '.button-bar', toggleButtonBarSelected)

});
