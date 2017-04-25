!function (document, window, $) {
    "use strict";
    $.validate({
        modules : 'date, security, file',
        onModulesLoaded : function() {
            $('#card').on('change', function() {
                var card = $(this).val();
                $('input[name="ccard_num"]').attr('data-validation-allowing', card);
            });
        }
    });
     // $('#area').restrictLength($('#maxlength'));
}(document, window, jQuery);
