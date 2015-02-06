$(document).foundation();

var sourceSwap = function () {
  var $this = $(this);
  var newSource = $this.data('alt-src');
  $this.data('alt-src', $this.attr('src'));
  $this.attr('src', newSource);
}

$(function() {
  $('img[data-alt-src]').each(function() {
      new Image().src = $(this).data('alt-src');
  }).hover(sourceSwap, sourceSwap);


  // LIST ITEM
  // -----------------
  // List item remove
  $('body').on('click', '.list-item-action[data-remove-this]', function (e) {
    var item = $(this).closest('.list-item.is-removable');
    var otherItems = item.siblings('.list-item.is-removable');
    if(otherItems.length > 1){
      item.remove();
    } else if(otherItems.length == 1) {
      otherItems.find('[data-remove-this]').hide();
      item.remove();
    }
  })
  // List item add
  .on('click', '.list-action [data-add-item]', function (e) {
    var container = $(this).closest('.list-action');
    var lastItem = container.prev('.list-item');
    lastItem.find('[data-remove-this]').show();
    lastItem.clone().insertBefore(container);
  })

  // BUTTON BAR
  // -----------------
  // Button bar select line
  .on('click', '.button-bar label', function (e) {
    var item = $(this).closest('.list-item');
    var selectedValue = $(this).prev('input[type="radio"]').val();
    if(selectedValue === 'none'){
      item.removeClass('is-selected');
    } else {
      item.addClass('is-selected');
    }
  });

});