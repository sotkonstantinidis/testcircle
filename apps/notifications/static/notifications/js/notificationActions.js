(function ($) {
    $.fn.bindNotificationActions = function(options) {

        var elem = this;

        // load initial data
        elem.load(options.notifications_url);

        // pagination
        $(this).on('click', 'ul.pagination li a', function(event) {
            $.ajax({
                url: event.target.href,
                method: 'GET'
            }).done(function (data) {
                elem.html(data);
            });
            return false;
        });

        // update 'is read' status on click
        $(this).on('click', '.mark-done', function(event) {
            $.ajax({
                url: options.read_url,
                method: 'POST',
                data: ({
                    user: options.user,
                    log: $(this).val(),
                    checked: $(this).is(':checked')
                })
            }).done(function () {
                $(event.target).closest('.notification-list').toggleClass('is-read');
            });
        });

    };
}(jQuery));
