!function (document, window, $) {
    "use strict";
    var $step = $('.step_with_progressbar ul li');
    $step.on('click',function(){
       var $this = $(this),
           $progressWidth = $this.data('width');
        $('.step_progressbar').children('div').css('width',$progressWidth);
        $step.removeClass('active');
        $this.addClass('active');
    });
}(document, window, jQuery);
