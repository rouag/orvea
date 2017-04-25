$(function () {
    "use strict";
    var doc = $('html, body');

    try {
        window.prettyPrint && prettyPrint();

        anchors.add('.bb-examples-list .bb-example');

        Example.init({
            "selector": ".bb-alert"
        });
    }
    catch (ex) {

    }

});

var Example = (function() {
    "use strict";

    var elem,
        hideHandler,
        that = {};

    that.init = function(options) {
        elem = $(options.selector);
    };

    that.show = function(text) {
        clearTimeout(hideHandler);

        elem.find("span").html(text);
        elem.delay(200).fadeIn().delay(4000).fadeOut();
    };

    return that;
}());

$('[data-plugin="bootbox"]').on('click', function () {
    var $this = $(this),
        $options = $.extend({}, $this.data()),
        $type = $options.type,
        $callback = $this.data('callback');

    if ($callback !== undefined) {
        $options.callback = window[$callback];
    }

    if ($type == "alert") {
        var $defaults = {buttons: {
                ok: {
                    className: 'btn-primary flat-buttons waves-effect waves-button'
                }
            }},
            $options2 = $.extend({},$defaults, $options);
        bootbox.alert($options2);
    } else if ($type == "confirm") {
        var $defaults = {buttons: {
                confirm: {
                    className: 'btn-success flat-buttons waves-effect waves-button'
                },
                cancel: {
                    className: 'btn-danger flat-buttons waves-effect waves-button'
                }
            }},
            $options2 = $.extend({},$defaults, $options);
        bootbox.confirm($options2);
    } else if ($type == "prompt") {
        var $defaults = {buttons: {
                confirm: {
                    className: 'btn-primary flat-buttons waves-effect waves-button'
                },
                cancel: {
                    className: 'btn-default flat-buttons waves-effect waves-button'
                }
            }},
            $options2 = $.extend({},$defaults, $options);
        bootbox.prompt($options2);
    } else {
        var $defaults = {buttons: {
                confirm: {
                    className: 'btn-primary flat-buttons waves-effect waves-button'
                },
                cancel: {
                    className: 'btn-default flat-buttons waves-effect waves-button'
                }
            }},
            $options2 = $.extend({},$defaults, $options);
        bootbox.dialog($options2);
    }
});

window.defaultalert = function () {
    Example.show('Default alert callback!');
}
window.callbackoption = function () {
    Example.show('This was logged in the callback!');
}
window.smallalert = function () {
    Example.show('Small alert shown');
}
window.largealert = function () {
    Example.show('Large alert shown');
}
window.overlayalert = function () {
    Example.show('Dismissable background alert shown');
}
window.bootboxConfirmCallback = function (result) {
    Example.show('This was logged in the callback: ' + result);
}
window.bootboxPromptCallback = function (result) {
    Example.show('This was logged in the callback: ' + result);
}

$("#bootboxCustomOption").on("click", function () {
    bootbox.confirm({
        message: "This is a confirm with custom button text and color! Do you like it?",
        buttons: {
            confirm: {
                label: 'Yes',
                className: 'btn-success flat-buttons waves-effect waves-button'
            },
            cancel: {
                label: 'No',
                className: 'btn-danger flat-buttons waves-effect waves-button'
            }
        },
        callback: function (result) {
            Example.show('This was logged in the callback: ' + result);
        }
    });
});
$("#bootboxConfirmText").on("click", function () {
    bootbox.confirm({
        title: "Destroy planet?",
        message: "Do you want to activate the Deathstar now? This cannot be undone.",
        buttons: {
            cancel: {
                label: '<i class="icon_close"></i> Cancel',
                className: 'btn-default flat-buttons waves-effect waves-button'
            },
            confirm: {
                label: '<i class="icon_check"></i> Confirm',
                className: 'btn-primary flat-buttons waves-effect waves-button'
            }
        },
        callback: function (result) {
            Example.show('This was logged in the callback: ' + result);
        }
    });
});

$("#bootboxpromptCheckbox").on("click", function () {
    bootbox.prompt({
        title: "This is a prompt with a set of checkbox inputs!",
        inputType: 'checkbox',
        buttons: {
            cancel: {
                className: 'btn-danger flat-buttons waves-effect waves-button'
            },
            confirm: {
                className: 'btn-success flat-buttons waves-effect waves-button'
            }
        },
        inputOptions: [
            {
                text: 'Choice One',
                value: '1',
            },
            {
                text: 'Choice Two',
                value: '2',
            },
            {
                text: 'Choice Three',
                value: '3',
            }
        ],
        callback: function (result) {
            Example.show('This was logged in the callback: ' + result);
        }
    });
});

$("#bootboxpromptselect").on("click", function () {
    bootbox.prompt({
        title: "This is a prompt with select!",
        inputType: 'select',
        buttons: {
            cancel: {
                className: 'btn-default flat-buttons waves-effect waves-button'
            },
            confirm: {
                className: 'btn-primary flat-buttons waves-effect waves-button'
            }
        },
        inputOptions: [
            {
                text: 'Choose one...',
                value: '',
            },
            {
                text: 'Choice One',
                value: '1',
            },
            {
                text: 'Choice Two',
                value: '2',
            },
            {
                text: 'Choice Three',
                value: '3',
            }
        ],
        callback: function (result) {
            Example.show('This was logged in the callback: ' + result);
        }
    });
});

$("#customDialogAsOverlay").on("click", function () {
    var timeout = 3000; // 3 seconds
    var dialog = bootbox.dialog({
        message: '<p class="text-center">Please wait while we do something...</p>',
        closeButton: false
    });
    setTimeout(function () {
        dialog.modal('hide');
    }, timeout);
});

$("#customDialogInit").on("click", function () {
    var dialog = bootbox.dialog({
        title: 'A custom dialog with init',
        message: '<p><i class="icon_cog"></i> Loading...</p>'
    });

    dialog.init(function () {
        setTimeout(function () {
            dialog.find('.bootbox-body').html('I was loaded after the dialog was shown!');
        }, 3000);
    });
});