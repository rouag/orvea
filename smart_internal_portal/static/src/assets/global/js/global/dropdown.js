!function (document, window, $) {
    "use strict";
    $(function () {
        $('#cd-dropdown').dropdown({
            gutter: 5,
            stack: false,
            delay: 100,
            slidingIn: 100
        });
        $('#cd-dropdown-first').dropdown({
            gutter: 5,
            stack: false,
            slidingIn: 100
        });
        $('#cd-dropdown-second').dropdown({
            gutter: 5
        });
        $('#cd-dropdown-third').dropdown();
    });

}(document, window, jQuery);
