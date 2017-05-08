/**
 * Select2 Arabic translation.
 *
 * Author: Adel KEDJOUR <adel@kedjour.com>
 */
(function ($) {
    "use strict";

    $.extend($.fn.select2.defaults, {
		formatMatches: function (matches) { if (matches === 1) { return "نتيجة واحدة هي المتاحة، اضغط دخول لتحديده."; } return matches + " نتائج متاحة, للتنقل بينها استخدم مفاتيح الأسهم أسفل/أعلى"; },
        formatNoMatches: function () { return "لم يتم العثور على مطابقات"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; if (n == 1){ return "الرجاء إدخال حرف واحد على الأكثر"; } return n == 2 ? "الرجاء إدخال حرفين على الأكثر" : "الرجاء إدخال " + n + " على الأكثر"; },
        formatInputTooLong: function (input, max) { var n = input.length - max; if (n == 1){ return "الرجاء إدخال حرف واحد على الأقل"; } return n == 2 ? "الرجاء إدخال حرفين على الأقل" : "الرجاء إدخال " + n + " على الأقل "; },
        formatSelectionTooBig: function (limit) { if (n == 1){ return "يمكنك أن تختار إختيار واحد فقط"; } return n == 2 ? "يمكنك أن تختار إختيارين فقط" : "يمكنك أن تختار " + n + " إختيارات فقط"; },
        formatLoadMore: function (pageNumber) { return "تحميل المزيد من النتائج…"; },
        formatSearching: function () { return "البحث…"; }
    });
})(jQuery);