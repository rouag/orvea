!function (window, document, $) {
    "use strict";
    var selector = '.message-data';
    jQuery(selector).on('click', function () {
        jQuery(selector).removeClass('active');
        jQuery(this).addClass('active');
    });
    jQuery('.message-data').on('click',function () {
        var img = jQuery(this).find("a .message-image img");
        var newSrc = img.attr("src");
        jQuery('.active-user').attr('src', newSrc);

    });
}(window, document, jQuery);