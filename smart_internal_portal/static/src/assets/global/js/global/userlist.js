!function (document, window, $) {
    "use strict";
    $(".openUserlist").on('click',function () {

        $(".overlay-userlistNav").addClass("open-userlist-section");
    });
    $(".closeUserlist").on('click',function () {

        $(".overlay-userlistNav").removeClass("open-userlist-section");
    });

    jQuery(document).on("click", "[data-toggle=edit]", function () {
        "use strict";


        $(".save-btn").toggleClass("active");
        $(".info-userlist").toggleClass("active"),

            $('.save-btn').html("Edit");
        $('.save-btn.active').html("Save");

    }),
        jQuery(document).on("change", ".info-userlist .userlist-group", function () {
            var $input = jQuery(this).find("input")
            var $textarea = jQuery(this).find("textarea"),
                $span = jQuery(this).siblings(".detail-profile");
            $span.html($input.val());
            $span.html($textarea.val());
        });

}(document, window, jQuery);
