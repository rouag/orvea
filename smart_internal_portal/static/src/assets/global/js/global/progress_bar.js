!function (window, document, $) {
    "use strict";

    jQuery('.vertical-top .progress-fill span').each(function(){
    var percent = jQuery(this).html();
    var pBottom = 100 - ( percent.slice(0, percent.length - 1) ) + "%";
        jQuery(this).parent().css({
        'height' : percent,
        'bottom' : pBottom,
        'top'    : 0
    });
});
    jQuery('.vertical-bottom .progress-fill span').each(function(){
    var percent = jQuery(this).html();
    var pTop = 100 - ( percent.slice(0, percent.length - 1) ) + "%";
        jQuery(this).parent().css({
        'height' : percent,
        'top' : pTop

    });
});
}(window, document, jQuery);