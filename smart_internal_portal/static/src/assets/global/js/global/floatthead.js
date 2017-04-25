!function (window, document, $) {
    "use strict";
    var $table = $('#floattheadtableBasic');
    $table.floatThead({
        top: function () {
            return $("#header").outerHeight()
        },
        resize: true,
        position: "absolute"
    });

    var $twindowsscroll = $('#floattheadtablescroll');
    $twindowsscroll.floatThead({
        top: function () {
            return $("#header").outerHeight()
        },
        resize: true,
        position: "absolute"
    });

    var $tablelazy = $('#floattheadwithlazy');
    $tablelazy.floatThead({
        top: function () {
            return $("#header").outerHeight()
        },
        resize: true,
        position: "absolute"
    });

    $('a.add-thead').on('click', function(e){
        $tablelazy.prepend('<thead><tr><th>Name</th><th>Position</th><th>Office</th><th>Salary</th></tr></thead>');
        $tablelazy.floatThead('reflow');
        e.preventDefault();
    });

}(window, document, jQuery);