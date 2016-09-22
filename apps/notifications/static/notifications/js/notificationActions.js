(function ($) {
    $.fn.bindNotificationActions = function(options) {

        var defaults = {
            initialParams: '',
            questionnaire: '',
            isTeaser: false
        };
        var settings = $.extend( {}, defaults, options );
        var elem = this;
        var page = 1;
        var isPending = false;  // see filter for pending.
        // var questionnaire = '';  // see filter for questionnaires.

        // load initial data
        elem.load(settings.notificationsUrl + settings.initialParams);

        // load data when clicking on pagination item
        elem.on('click', 'ul.pagination li a', function(event) {
            page = $(this).attr('href');
            $.ajax({
                url: get_url(),
                method: 'GET'
            }).done(function (data) {
                elem.html(data);
            });
            return false;
        });

        // update 'is read' status on click
        elem.on('click', '.mark-done', function(event) {
            $.ajax({
                url: settings.readUrl,
                method: 'POST',
                data: ({
                    user: settings.user,
                    log: $(this).val(),
                    checked: $(this).is(':checked')
                })
            }).done(function () {
                $(event.target).closest('.notification-list').toggleClass('is-read');
            });
        });

        // filter 'pending' only
        elem.on('click', '#is-pending', function() {
            elem.html(settings.spinner);
            isPending = $(this).is(':checked');
            page = 1;
            $.ajax({
              url: get_url(),
              method: 'GET'
            }).done(function(data) {
              elem.html(data);
            });
        });

        // handle filters for pending and questionnaires
        elem.on('click', '#questionnaire-filter-toggler', function() {
            $('#questionnaire-filter').toggle(
            function() {
                $(this).addClass('hide');
            }, function() {
                var select = $(this).children('select').first();
                // only load options if not in dom already - two options may be
                // present already ('all' and selected element).
                if (select.children('option').length < 3) {
                    $.ajax({
                        url: settings.questionnairesUrl,
                        method: 'get',
                        contentType: 'json'
                    }).done(function(data) {
                        $.each(data['questionnaires'], function(i, questionnaire) {
                            select.append(
                                '<option value="' + questionnaire + '">' +
                                questionnaire + '</option>'
                            );
                        });
                        select.chosen();
                        select.on('change', function(evt, params) {
                            page = 1;
                            settings.questionnaire = params['selected'];
                            $.ajax({
                              url: get_url(),
                              method: 'GET'
                            }).done(function(data) {
                              elem.html(data);
                            });
                        });
                    });
                }
                $(this).removeClass('hide');
            });
        });

        /**
         * Helper to create the proper url depending on state of 'pending'
         * and 'questionnaire'
         * @returns {string}
         */
        function get_url() {
            var url = settings.notificationsUrl + '?page=' + page;

            if (settings.isTeaser) url += '&is_teaser';

            var isPendingDOM = $('#is-pending').is(':checked');
            if (isPending || isPendingDOM) url += '&is_pending';

            if (settings.questionnaire != '') {
                url += '&questionnaire=' + settings.questionnaire;
            }
            return url
        }
    };
}(jQuery));
