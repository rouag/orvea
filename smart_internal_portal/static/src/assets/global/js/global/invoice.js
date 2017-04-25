!function (document, window, $) {
    "use strict";
    $(".invoice-print").on('click', function() {
        $("#invoice-page").print();
    });
}(document, window, jQuery);