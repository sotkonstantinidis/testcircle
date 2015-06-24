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
