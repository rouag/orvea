!function (document, window, $) {
    "use strict";

    if (typeof Waves !== 'undefined') {
        Waves.attach('.flat-buttons', ['waves-button']);
        Waves.attach('.float-buttons', ['waves-button', 'waves-float']);
        Waves.attach('.float-button-light', ['waves-button', 'waves-float', 'waves-light']);
        Waves.attach('.flat-icon', ['waves-circle']);
        Waves.attach('.float-icon', ['waves-circle', 'waves-float']);
        Waves.attach('.float-icon-light', ['waves-circle', 'waves-float', 'waves-light']);
        Waves.init();
    }
}(document, window, jQuery);
