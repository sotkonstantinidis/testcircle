function addFormset(selector, type) {
    /**
        Inspired by: http://stackoverflow.com/a/669982/841644
    */
    var newElement = $(selector+':last').clone(true);
    var total = $(selector).length;
    var max = $('#id_' + type + '-MAX_NUM_FORMS').val();
    if (total >= max) return;
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}
