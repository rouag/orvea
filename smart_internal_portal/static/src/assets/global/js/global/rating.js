!function (document, window, $) {
    "use strict";

    $('[data-plugin="rating"]').each(function () {
        var $this = $(this),
            $options = $.extend({}, $this.data());
        $this.starRating($options);
    });
    function callback(currentRating, $el) {
        alert('rated ', currentRating);
        console.log('DOM element ', $el);
    };

    $(".my-rating-7").starRating({
        initialRating: 2.5,
        starSize: 20,
        hoverColor: '#57bbc7',
        disableAfterRate: false,
        onHover: function (currentIndex, currentRating, $el) {
            $('.live-rating').text(currentIndex);
        },
        onLeave: function (currentIndex, currentRating, $el) {
            $('.live-rating').text(currentRating);
        }
    });

    $('[data-plugin="Jrating"]').each(function () {
        var $this = $(this),
            $options = $.extend({}, $this.data());
        $options.icon = $this.data('icons');
        $this.addRating($options);
    });

}(document, window, jQuery);
