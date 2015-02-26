// WIZARD
// -----------------
// Next / Previous step


/**
 * Updates the process indicators while entering the form. Updates the
 * number of subcategories filled out and the progress bar.
 */
function watchFormProgress() {
  var completed = 0;
  $('fieldset.row').each(function() {
    var content = false;
    // Textfields and Textareas
    $(this).find('div.row.list-item input:text, div.row.list-item textarea').each(function() {
      if ($(this).is(":visible") && $(this).val() != '') {
        content = true;
        return;
      }
    });
    // Radio
    $(this).find('div.row.list-item input:radio').each(function() {
      if ($(this).is(':checked') && $(this).val() != '') {
        content = true;
        return;
      }
    });
    // Checkbox
    $(this).find('div.row.list-item input:checkbox').each(function() {
      if ($(this).is(':checked')) {
        content = true;
        return
      }
    });
    if (content) {
      completed++;
    }
  });
  var stepsElement = $('.progress-completed');
  stepsElement.html(completed);
  var total = stepsElement.next('.progress-total').html();
  var progress = completed / total * 100;
  var progressbar = stepsElement.siblings('.progress');
  progressbar.find('.meter').width(progress + '%');
}

$(function() {

  // Initial form progress
  watchFormProgress();

  // Initial button bar selected toggle
  $('.button-bar').each(toggleButtonBarSelected);

  // Form progress upon input
  $('fieldset.row div.row.list-item').on('change', function() {
    watchFormProgress();
  });

  $('body').on('click', '[data-magellan-step]', function (e) {

    e.preventDefault();
    var expedition = $(this),
        hash = this.hash.split('#').join(''),
        target = $("a[name='"+hash+"']"),
        currentNumber = parseInt(hash.substr(hash.length - 1)),
        nextNumber = currentNumber,
        maxSteps = $("a[name^='question']").length;

    if (target.length != 0) {
      // Account for expedition height if fixed position
      var scroll_top = target.offset().top - 20 + 1;
      scroll_top = scroll_top - expedition.outerHeight();

      $('html, body').stop().animate({
        'scrollTop': scroll_top
      }, 700, 'swing', function () {
        if(history.pushState) {
          history.pushState(null, null, '#'+hash);
        } else {
          location.hash = '#'+hash;
        }
      });

      // Change Previous / Next href attr to point to the correct sections
      var nextNumber = currentNumber;
      if (currentNumber-1 > 0) {
        previous = 'question' + (currentNumber - 1);
        $('[data-magellan-step="previous"]').attr('href', '#'+previous);
      }
      if (currentNumber < maxSteps) {
        next = 'question' + (currentNumber + 1);
        $('[data-magellan-step="next"]').attr('href', '#'+next);
      }
    }
  })
  //  TODO - focus on current step (when location hash is changing)
  // // Bind the event.
  // $(window).on('hashchange', function() {
  //   // Alerts every time the hash changes!
  //   console.log( location.hash );
  // })

});
