!function (document, window, $) {
    "use strict";
    // mouse-on example
    var mouseOnDiv = $('#mouseon-examples div');
    var tipContent = $(
        '<p><b>Here is some content</b></p>'
    );
    mouseOnDiv.data('powertipjq', tipContent);
    mouseOnDiv.powerTip({
        placement: 'e',
        mouseOnToPopup: true
    });


    $('#api-open').on('click', function () {
        $.powerTip.show($('#mouseon-examples div'));
    });
    $('#api-close').on('click', function () {
        $.powerTip.hide();
    });
    $('#api-manual')
        .powerTip({
            manual: true
        })
        .on('click', function () {
            $(this).powerTip('show');
        })
        .on('mouseleave', function () {
            $(this).powerTip('hide', true);
        });
    $('#api-manual-mouse')
        .on('mouseenter', 'input', function (evt) {
            if (!$(this).data('powertip')) {
                $(this)
                    .data('powertip', 'Tooltip added: ' + (new Date()))
                    .powerTip({
                        manual: true
                    });
            }
            $(this).powerTip('show', evt);
        })
        .on('mouseleave', 'input', function () {
            $(this).powerTip('hide');
        });

}(document, window, jQuery);
