!function (document, window, $) {
    "use strict";
    $(document).on("click", "[data-toggle=edit]", function () {
        "use strict";
        $(".save-btn").toggleClass("active");
        $(".contact-info").toggleClass("active");
        $('.save-btn').html("Edit");
        $('.save-btn.active').html("Save");
    }),
        $(document).on("change", ".contact-info .form-group", function () {
            var $input = $(this).find("input"),
                $span = $(this).siblings("span");
            $span.html($input.val());
        });

    jQuery('.contact-delete').on('click', function () {
        jQuery(this).closest('.contacts').remove();
    });
}(document, window, jQuery);