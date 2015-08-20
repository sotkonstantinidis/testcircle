// WIZARD
// -----------------
// Next / Previous step

/**
 * Loop through the form fields of a subcategory to find out if they are
 * empty or if they contain values.
 *
 * @param {Element} element - An element containing the form fields, for
 *   example the subcategory fieldset.
 */
function hasContent(element) {
  var content = false;
  // Textfields and Textareas
  $(element).find('div.row.list-item input:text, div.row.list-item textarea').each(function() {
    if ($(this).is(":visible") && $(this).val() != '') {
      content = true;
      return;
    }
  });
  // Radio
  $(element).find('div.row.list-item input:radio').each(function() {
    if ($(this).is(':checked') && $(this).val() != '') {
      content = true;
      return;
    }
  });
  // Checkbox
  $(element).find('div.row.list-item input:checkbox').each(function() {
    if ($(this).is(':checked')) {
      content = true;
      return;
    }
  });
  // Image
  $(element).find('div.image-preview').each(function() {
    if ($(this).find('img').length) {
      content = true;
      return;
    }
  });
  // Select
  $(element).find('div.row.list-item select').each(function() {
    if ($(this).find(':selected').val()) {
      content = true;
      return;
    }
  });
  return content;
}


/**
 * Updates the process indicators while entering the form. Updates the
 * number of subcategories filled out and the progress bar.
 */
function watchFormProgress() {
  var completed = 0;
  $('fieldset.row').each(function() {
    var content = hasContent(this);
    if (content) {
      completed++;
    }
  });
  var stepsElement = $('.progress-completed');
  stepsElement.html(completed);
  var total = stepsElement.next('.progress-total').html();
  var progress = completed / total * 100;
  $('header.wizard-header').find('.meter').width(progress + '%');
}

/**
 * Check for additional questiongroups ("plus" questions) and hide them
 * initially if they are empty.
 */
function checkAdditionalQuestiongroups() {
  $('.plus-questiongroup div.content').each(function() {
    $(this).toggleClass('active', hasContent(this));
  });
}


/**
 * Checks conditional questiongroups and shows or hides questiongroups
 * based on an input value condition.
 *
 * @param {Element} element - The input element triggering the
 *   questiongroup.
 */
function checkConditionalQuestiongroups(element) {

  // Collect all the conditions for a questiongroup as they must all be
  // fulfilled and group them by questiongroup identifier.
  var all_conditions = $(element).data('questiongroup-condition').split(',');
  var conditionsByQuestiongroup = {};
  for (var i = all_conditions.length - 1; i >= 0; i--) {
    condition = all_conditions[i].split('|');
    if (condition.length !== 2) return;
    if (conditionsByQuestiongroup[condition[1]]) {
      conditionsByQuestiongroup[condition[1]].push(condition[0]);
    } else {
      conditionsByQuestiongroup[condition[1]] = [condition[0]];
    }
  }

  // Collect all the input fields with the same name, which is important
  // for example for checkboxes.
  allElements = $('[name="' + $(element).attr('name') + '"]');

  // For each conditional questiongroup, check if one of the form
  // elements with the given name fulfills all the conditions. If this
  // is true, then show the conditional questiongroup.
  for (var questiongroup in conditionsByQuestiongroup) {
    var currentConditions = conditionsByQuestiongroup[questiongroup];
    var currentConditionsFulfilled = false;

    allElements.each(function() {
      var currentElement = $(this);
      var val = null;

      var inputType = currentElement.attr('type');
      if ((inputType == 'radio' || inputType == 'checkbox') && currentElement.is(':checked')) {
        val = currentElement.val();
      } else if (inputType == 'text') {
        val = currentElement.val();
      }

      var conditionsFulfilled = val !== null && val !== '';
      if (val) {
        for (var c in currentConditions) {
          if (parseInt(val)) {
            var e = val + currentConditions[c];
          } else {
            var e = '"' + val + '"' + currentConditions[c];
          }
          conditionsFulfilled = conditionsFulfilled && eval(e);
        }
      }

      currentConditionsFulfilled = currentConditionsFulfilled || conditionsFulfilled;
    });

    var questiongroupContainer = $('#' + questiongroup);
    questiongroupContainer.toggle(currentConditionsFulfilled);
    if (!currentConditionsFulfilled) {
      clearQuestiongroup(questiongroupContainer);
    }
  }
}


/**
 * Remove a linked Questionnaire from the form. This is the action
 * triggered when clicking the "close" button in the link form. Removes
 * the display entry of the linked questionnaire as well as the hidden
 * input field for the form.
 *
 * @param {Element} el - The close button element. Needs to have the
 *   identifier of the link stored as data attribute.
 */
function removeLinkedQuestionnaire(el) {
  var fieldset = $(el).parents('fieldset');
  var identifier = $(el).data('input-hidden');
  $('#' + identifier).remove();
  $(el).parent('div.alert-box').remove();
  if (!fieldset.find('input[type="hidden"]').length) {
    fieldset.find('.empty').show();
  }
  return false;
}


/**
 * Clears all form fields of a questiongroup. It is important to trigger
 * the change event for each so chained conditional questiongroups are
 * validated.
 *
 * @param {Element} questiongroup - The questiongroup element in which
 *   to clear all fields.
 */
function clearQuestiongroup(questiongroup) {
  questiongroup.find('input:text, textarea').val('').change();
  questiongroup.find('input:radio').prop('checked', false).change();
  questiongroup.find('input:checkbox').prop('checked', false).change();
}

$(function() {

  $('body')
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
    var doNumberingUpdate = false;
    if (!lastItem.length) {
      // The element might be numbered, in which case it needs to be
      // accessed differently
      if (container.parent('.questiongroup-numbered-prefix').length) {
        lastItem = container.prev('.row');
        doNumberingUpdate = true;
      }
    }
    if (!lastItem.length) return;

    newElement = lastItem.clone();

    updateFieldsetElement(newElement, qg, currentCount, true);
    newElement.insertBefore(container);

    currentCount++;
    $('#id_' + qg + '-TOTAL_FORMS').val(currentCount);
    $(this).toggle(currentCount < maxCount);

    if (doNumberingUpdate) {
      updateNumbering();
    }
  })

  // Helptext: Toggle buttons (Show More / Show Less)
  .on('click', '.help-toggle-more', function(e) {
    var more = $(this).siblings('.help-content-more');
    var first = $(this).siblings('.help-content-first');
    if (more.is(':visible')) {
      // Hide "More"
      $(this).html($(this).data('text-more'));
      more.slideToggle(400, function() { first.toggle(); });
    } else {
      // Show "More"
      $(this).html($(this).data('text-first'));
      more.slideToggle();
      first.toggle();
    }
  })

  // BUTTON BAR
  // -----------------
  // Button bar select line
  .on('click', '.button-bar', toggleButtonBarSelected);

  // Initial form progress
  watchFormProgress();

  // Initial button bar selected toggle
  $('.button-bar').each(toggleButtonBarSelected);

  // Conditional questiongroups
  $('[data-questiongroup-condition]')
    .each(function() {
      checkConditionalQuestiongroups(this);
    })
    .on('change', function() {
      checkConditionalQuestiongroups(this);
    })
    .on('input', function() {
      checkConditionalQuestiongroups(this);
    });

  checkAdditionalQuestiongroups();

  // Form progress upon input
  $('fieldset.row div.row.list-item').on('change', function() {
    watchFormProgress();
  });

  // Select inputs with chosen
  $(".chosen-select").chosen();

  $('.sortable').sortable({
    handle: '.questiongroup-numbered-number',
    placeholder: 'sortable-placeholder',
    forcePlaceholderSize: true,
    stop: updateNumbering
  });

  // Search a linked Questionnaire through AJAX autocomplete.
  if ($.fn.autocomplete) {
    $('.link_search_field').autocomplete({
      source: function(request, response) {
        var translationNoResults = $(this.element).data('translation-no-results');
        var translationTooManyResults = $(this.element).data('translation-too-many-results');
        // AJAX call to the respective link search view.
        $.ajax({
          url: $(this.element).data('url'),
          dataType: 'json',
          data: {
            q: request.term
          },
          success: function(data) {
            if (!data.data.length) {
              // No results
              var result = [
                {
                  name: translationNoResults,
                  code: ''
                }
              ];
              response(result);
            } else {
              var res = data.data;
              if (data.total > 10) {
                // Too many results
                res = res.slice(0, 10);
                res.push({
                  name: translationTooManyResults,
                  code: ''
                });
              }
              response(res);
            }
          }
        });
      },
      create: function () {
        // Prepare the entries to display the name and code.
        $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
          return $('<li>')
                  .append('<a><strong>' + item.name + '</strong><br><i>' + item.code + '</i></a>')
                  .appendTo(ul);
              };
          },
      select: function( event, ui ) {
        if (!ui.item.value) {
          // No value (eg. when clicking "No results"), do nothing
          return false;
        }
        // Add hidden input field with ID.
        var keyword = $(this).data('keyword');
        var id = 'links__' + keyword + '__' + ui.item.id;
        if ($('#' + id).length) {
          // Do not add the link a second time if it is already there
          return false;
        }
        var hidden_input = $('<input id="' + id + '" type="hidden" name="links__' + keyword + '" />').val(ui.item.id);
        $(this).parent('fieldset').find('div.links').append(hidden_input);

        // Add name field
        $(this).parent('fieldset').find('div.links').append(
          '<div class="alert-box secondary">' + ui.item.name + '<a href="#" class="close" data-input-hidden="' + id + '">&times;</a></div>');
        $('div.links a.close').click(function() {
          removeLinkedQuestionnaire(this);
        });

        // Hide empty message
        $(this).parent('fieldset').find('.empty').hide();

        $(this).val('');
        return false;
      },
      minLength: 3
    });
    $('.ui-autocomplete').addClass('f-dropdown');
  }

  // Remove linked questionnaires
  $('div.links a.close').click(function() {
    removeLinkedQuestionnaire(this);
  });

  $('body').on('click', '[data-magellan-step]', function(e) {

      e.preventDefault();
      var expedition = $(this),
        hash = this.hash.split('#').join(''),
        target = $("a[name='" + hash + "']"),
        currentNumber = parseInt(hash.substr(hash.length - 1)),
        nextNumber = currentNumber,
        maxSteps = $("a[name^='question']").length;

      if (target.length != 0) {
        // Account for expedition height if fixed position
        var scroll_top = target.offset().top - 20 + 1;
        scroll_top = scroll_top - expedition.outerHeight();

        $('html, body').stop().animate({
          'scrollTop': scroll_top
        }, 700, 'swing', function() {
          if (history.pushState) {
            history.pushState(null, null, '#' + hash);
          } else {
            location.hash = '#' + hash;
          }
        });

        // Change Previous / Next href attr to point to the correct sections
        var nextNumber = currentNumber;
        if (currentNumber - 1 > 0) {
          previous = 'question' + (currentNumber - 1);
          $('[data-magellan-step="previous"]').attr('href', '#' + previous);
        }
        if (currentNumber < maxSteps) {
          next = 'question' + (currentNumber + 1);
          $('[data-magellan-step="next"]').attr('href', '#' + next);
        }
      }
    })
    //  TODO - focus on current step (when location hash is changing)
    // // Bind the event.
    // $(window).on('hashchange', function() {
    //   // Alerts every time the hash changes!
    //   console.log( location.hash );
    // })

  /**
   * DropzoneJS file upload.
   */
  var dropzones = [];

  $('.dropzone').each(function() {

    var dropzoneContainer = $(this);
    var previewContainer = $(this).data('upload-preview-container');
    if (previewContainer) {
      previewContainer = $('#' + previewContainer);
      previewContainer.on('mouseover', function() {
        $(this).find('.remove-image').toggle(true);
      }).on('mouseout', function() {
        $(this).find('.remove-image').toggle(false);
      });

      previewContainer.find('.remove-image').click(function() {
        /**
         * It is necessary to find the correct dropzone as there can be
         * multiple on the same page.
         */
        var dropzone = null;

        var dropzoneId = $(this).data('dropzone-id');
        for (var d in dropzones) {
          if (dropzones[d].element.id === dropzoneId) {
            dropzone = dropzones[d];
          }
        }

        if (dropzone) {
          var files = dropzone.files;
          for (var f in files) {
            dropzone.removeFile(files[f]);
          }
          previewContainer.toggle();
          dropzoneContainer.toggle();
          previewContainer.find('.image-preview').empty();
        }
        watchFormProgress();
        return false;
      });
    }

    var url = dropzoneContainer.data('upload-url');

    if (!url) {
      return;
    }

    new Dropzone(this, {
      url: url,
      addRemoveLinks: true,
      init: function() {
        dropzones.push(this);
        $(this.hiddenFileInput).attr(
          'id', this.element.id.replace('file_', 'hidden_'));
        if (previewContainer) {
          var el = $('input#' + this.element.id.replace('file_', ''));
          if (el.val()) {

            $.ajax({
              url: '/questionnaire/file/interchange/' + el.val()
            }).done(function(interchange) {
              addImage(previewContainer, dropzoneContainer, interchange);
              watchFormProgress();
            });
          }
        }
      },
      sending: function(file, xhr, formData) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      },
      success: function(file, response) {
        if (previewContainer && response['interchange']) {
          addImage(previewContainer, dropzoneContainer,
            response['interchange']);
        }
        watchFormProgress();
        addFilename(response['uid'], file, this);
      },
      error: function(file, response) {
        this.removeFile(file);
        if (previewContainer) {
          dropzoneContainer.toggle();
          previewContainer.toggle();
          previewContainer.find('.image-preview').empty();
        }
        watchFormProgress();
        showUploadErrorMessage(response['msg']);
      },
      removedfile: function(file) {
        removeFilename(file, this);
        var _ref;
        return (_ref = file.previewElement) != null ? _ref.parentNode.removeChild(file.previewElement) : void 0;
      }
    });
  });
});

/**
 * Add an image to the preview container. This is done by creating an
 * image element and adding the interchange attribute.
 *
 * @param {element} previewContainer - The preview container to add the
 *   image to. This element will be made visible.
 * @param {element} dropzoneContainer - The dropzone container which
 *   will be hidden.
 * @param {string} interchangeData - The interchange data.
 */
function addImage(previewContainer, dropzoneContainer, interchangeData) {
  var img = $(document.createElement('img'));
  img.attr('data-interchange', interchangeData);
  img.css({'width': '100%'});
  previewContainer.find('.image-preview').html(img);
  $(document).foundation();
  $(document).foundation('interchange', 'reflow');
  dropzoneContainer.toggle();
  previewContainer.toggle();
}

/*
 * Add a filename to the hidden form input field after upload of the
 * file. Also stores the filename to the file so it can later be
 * retrieved.
 *
 * @param {string} filename - The filename of the uploaded file as
 *  returned by the server.
 * @param {file} file - The uploaded file.
 * @param {Element} dropzone - The dropzone element.
 */
function addFilename(filename, file, dropzone) {
  file.filename = filename;
  var el = $('input#' + dropzone.element.id.replace('file_', ''));
  var vals = [];
  if (el.val()) {
    vals = el.val().split(',');
  }
  vals.push(filename);
  el.val(vals.join(','));
}

/*
 * Remove a filename from the hidden form input field after removing the
 * file from the dropzone.
 *
 * @param {file} file - The file to be removed.
 * @param {Element} dropzone - The dropzone element.
 */
function removeFilename(file, dropzone) {
  var el = $('input#' + dropzone.element.id.replace('file_', ''));
  var vals = [];
  if (el.val()) {
    vals = el.val().split(',');
  }
  for (var v in vals) {
    if (vals[v] == file.filename) {
      vals.splice(v, 1);
    }
  }
  el.val(vals.join(','));
}

/*
 * Show an error message if the file upload failed.
 *
 * @param {string} message - The error message returned by the server if
 *  available.
 */
function showUploadErrorMessage(message) {
  if (message) {
    alert('Error: ' + message);
  } else {
    alert('An error occurred while uploading the file.');
  }
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
      var id = $(this).attr('id').replace(id_regex, replacement);
      $(this).attr({'name': name, 'id': id});
    });
    element.find('label').each(function() {
        var newFor = $(this).attr('for').replace(id_regex, replacement);
        $(this).attr('for', newFor);
    });
  if (reset) {
    clearQuestiongroup(element);
  }
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
