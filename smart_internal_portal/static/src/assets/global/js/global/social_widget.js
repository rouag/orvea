!function (document, window, $) {
    "use strict";
    var $defaults = {
        time: "icon icon_clock",
        date: "icon icon_calendar",
        up: "icon arrow_carrot-up",
        down: "icon arrow_carrot-down",
        previous: 'icon arrow_carrot-left',
        next: 'icon arrow_carrot-right',
    };

    $("#owl-full").owlCarousel({
        navigation: true,
        slideSpeed: 400,
        rtl:true,
        paginationSpeed: 500,
        items: 1
    });
}(document, window, jQuery);
