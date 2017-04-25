!function (document, window, $) {
    "use strict";

    $('#external-events .fc-event').each(function () {

        $(this).data('event', {
            title: $.trim($(this).text()),
            stick: true
        });

        $(this).draggable({
            zIndex: 999,
            revert: true,
            revertDuration: 0
        });

    });

    $('#calendar').fullCalendar({
        events: [
            {
                title: 'All Day Event',
                start: '2016-12-20'
            },
            {
                title: 'Hour',
                start: '2016-12-12T17:30:00'
            }],
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        editable: true,
        droppable: true,
        drop: function () {
            if ($('#drop-remove').is(':checked')) {
                $(this).remove();
            }
        }
    });

}(document, window, jQuery);
