!function (document, window, $) {
    "use strict";
    $('.btn-change').on('click', function() {
        var $height = $("#height").val();
        if($height){
            changeSize();
        }
    });
    function changeSize() {
        var height = $("#height").val();

        $("#update").height(height);

        // update scrollbars
        $("#update").perfectScrollbar('update');
    }
}(document, window, jQuery);
