!function (document, window, $) {
    "use strict";
    function deselect(e) {
        $('.pop').slideFadeToggle(function () {
            e.removeClass('selected');
        });
    }

    $('.mail_compose_btn').on('click', function () {
        if ($(window).width() < 767) {
            if (!$('.mail-toggle').hasClass('collapsed')) {
                $('.mail-toggle').click();
            }
        }

        if ($(this).hasClass('selected')) {
            deselect($(this));
        } else {
            $(this).addClass('selected');
            $('.pop').slideFadeToggle();
        }
        return false;
    });


    $('.compose_close').on('click', function () {
        deselect($('#compose_mail'));
        return false;
    });
    $.fn.slideFadeToggle = function (easing, callback) {
        return this.animate({opacity: 'toggle', height: 'toggle'}, 'fast', easing, callback);
    };
    /* mail reply */
    $("#mail_reply").on('click', function () {
        $('.forward_block').removeClass('show_forward');
        $('.reply_main_block').toggleClass('show_relpy');
    });
    $("#mail_reply_cancel").on('click', function () {
        $('.reply_main_block').removeClass('show_relpy');
    });
    /* mail forward */
    $("#mail_forward_btn").on('click', function () {
        $('.reply_main_block').removeClass('show_relpy');
        $('.forward_block').toggleClass('show_forward');
        $('#forward-mail').children('.CodeMirror').children('div').trigger('click');
    });
    $("#mail_forward_cancel").on('click', function () {
        $('.forward_block').removeClass('show_forward');
    });

    $('.mail_favorite a').on('click', function () {
        var $this = $(this);
        $this.toggleClass('rated');
    });

    $(".check_all").on('change', function (e) {
        var $this = $(this);
        if ($this.is(':checked') === true) {
            $this.parents('div#individualcolumn_wrapper').find('[type="checkbox"]').prop('checked', true);
        }
        else {
            $this.parents('div#individualcolumn_wrapper').find('[type="checkbox"]').prop('checked', false);
        }
    });

}(document, window, jQuery);

function stikysidebar() {
    $(window).scroll(function () {
        if ($(window).width() <= 767) {
            var scroll = $(window).scrollTop(),
                $mailtoggle = $('.mail-toggle').outerHeight() + 30,
                $sitetitle = $('.site-content-title').outerHeight();
            if (scroll >= $sitetitle) {
                $("body").addClass("sticky_sidebar").css('margin-top', $mailtoggle);
            } else {
                $("body").removeClass("sticky_sidebar").css('margin-top', '0');
            }
        }else{
            $("body").removeClass("sticky_sidebar").removeAttr("style");
        }
    });
}

stikysidebar();

$(window).resize(function () {
    stikysidebar();
});
