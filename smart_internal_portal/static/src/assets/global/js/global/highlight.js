!function (document, window, $) {
    "use strict";
    $('pre code').each(function(i, block) {
        hljs.highlightBlock(block);
    });
}(document, window, jQuery);
