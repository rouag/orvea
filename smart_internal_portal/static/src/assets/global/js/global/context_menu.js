!function (window, document, $) {
    "use strict";
    $('[data-plugin="contextmenu"]').each(function(){
        var $this = $(this),
            $defaults = {
                "items": {
                    "edit": {name: "Edit", icon: "edit"},
                    "cut": {name: "Cut", icon: "cut"},
                    "copy": {name: "Copy", icon: "copy"},
                    "paste": {name: "Paste", icon: "paste"},
                    "delete": {name: "Delete", icon: "delete"},
                    "sep1": "---------",
                    "quit": {name: "Quit", icon: function(){
                        return 'context-menu-icon context-menu-icon-quit';
                    }}
                }},
            $options = $.extend({},$defaults, $this.data());
        $this.contextMenu(this,$options);
    });
    $.contextMenu({
        selector: '.context-menu-default',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {name: "Edit", icon: "edit"},
            "cut": {name: "Cut", icon: "cut"},
            copy: {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "quit": {name: "Quit", icon: function(){
                return 'context-menu-icon context-menu-icon-quit';
            }}
        }
    });

    var errorItems = { "errorItem": { name: "Items Load error" },};
    var loadItems = function () {
        var dfd = jQuery.Deferred();
        setTimeout(function () {
            dfd.resolve(subItems);
        }, 2000);
        return dfd.promise();
    };

    var subItems = {
        "sub1": { name: "Submenu1", icon: "edit" },
        "sub2": { name: "Submenu2", icon: "cut" },
    };

    $.contextMenu({
        selector: '.context-menu-loading',
        build: function ($trigger, e) {
            return {
                callback: function (key, options) {
                    var m = "clicked: " + key;
                    console.log(m);
                },
                resize:true,
                items: {
                    "edit": { name: "Edit", icon: "edit" },
                    "cut": { name: "Cut", icon: "cut" },
                    "status": {
                        name: "Status",
                        icon: "delete",
                        items: loadItems(),
                    },
                    "normalSub": {
                        name: "Normal Sub",
                        items: {
                            "normalsub1": { name: "normal Sub 1"},
                            "normalsub2": { name: "normal Sub 2"},
                            "normalsub3": { name: "normal Sub 3" },
                        }
                    }
                }
            };
        }
    });

    //normal promise usage example
    var completedPromise = function (status) {
        console.log("completed promise:", status);
    };

    var failPromise = function (status) {
        console.log("fail promise:", status);
    };

    var notifyPromise = function (status) {
        console.log("notify promise:", status);
    };

    $.loadItemsAsync = function() {
        console.log("loadItemsAsync");
        var promise = loadItems();
        $.when(promise).then(completedPromise, failPromise, notifyPromise);
    };

    $.contextMenu({
        selector: '.context-menu-sub',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {"name": "Edit", "icon": "edit"},
            "cut": {"name": "Cut", "icon": "cut"},
            "sep1": "---------",
            "quit": {"name": "Quit", "icon": "quit"},
            "sep2": "---------",
            "fold1": {
                "name": "Sub group",
                "items": {
                    "fold1-key1": {"name": "Sub group"},
                    "fold1-key2": {"name": "Sub group"},
                    "fold1-key3": {"name": "Sub group"}
                }
            },
            "fold1a": {
                "name": "Other group",
                "items": {
                    "fold1a-key1": {"name": "Other 1"},
                    "fold1a-key2": {"name": "Other 2"},
                    "fold1a-key3": {"name": "Other 3"}
                }
            }
        }
    });


    /**************************************************
     * Custom Command Handler
     **************************************************/
    $.contextMenu.types.label = function(item, opt, root) {
        // this === item.$node

        $('<span>Label<ul>'
            + '<li class="label1 btn-primary" title="primary">label 1'
            + '<li class="label2 btn-danger" title="danger">label 2'
            + '<li class="label3 btn-success" title="success">label 3'
            + '<li class="label4 btn-warning" title="warning">label 4'
            + '<li class="label5 btn-info" title="info">label 5')
            .appendTo(this)
            .on('click', 'li', function() {
                // do some funky stuff
                console.log('Clicked on ' + $(this).text());
                // hide the menu
                root.$menu.trigger('contextmenu:hide');
            });

        this.addClass('labels').on('contextmenu:focus', function(e) {
            // setup some awesome stuff
        }).on('contextmenu:blur', function(e) {
            // tear down whatever you did
        }).on('keydown', function(e) {
            // some funky key handling, maybe?
        });
    };

    /**************************************************
     * Context-Menu with custom command "label"
     **************************************************/
    $.contextMenu({
        selector: '.context-menu-label',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            open: {name: "Open", callback: $.noop},
            label: {type: "label", customName: "Label"},
            edit: {name: "Edit", callback: $.noop}
        }
    });

    $.contextMenu({
        selector: '.context-menu-disabled',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {name: "Clickable", icon: "edit", disabled: false},
            "cut": {name: "Disabled", icon: "cut", disabled: true}
        }
    });

    $.contextMenu({
        selector: '.context-menu-disblecall',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {name: "Clickable", icon: "edit", disabled: false},
            "cut": {name: "Disabled", icon: "cut", disabled: true}
        }
    });



    $('#activate-menu').on('click', function(e) {
        e.preventDefault();
        $('.context-menu-activated').contextMenu();
        // or $('.context-menu-default').trigger("contextmenu");
        // or $('.context-menu-default').contextMenu({x: 100, y: 100});
    });

    $.contextMenu({
        selector: '.context-menu-activated',
        trigger: 'none',
        resize:true,
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        items: {
            "edit": {name: "Edit", icon: "edit"},
            "cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "quit": {name: "Quit", icon: function($element, key, item){ return 'context-menu-icon context-menu-icon-quit'; }}
        }
    });


    $.contextMenu({
        selector: '.context-menu-hovactive',
        trigger: 'hover',
        delay: 500,
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {name: "Edit", icon: "edit"},
            "cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "quit": {name: "Quit", icon: function($element, key, item){ return 'context-menu-icon context-menu-icon-quit'; }}
        }
    });

    $.contextMenu({
        selector: '.context-menu-autohide',
        trigger: 'hover',
        delay: 500,
        autoHide: true,
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {name: "Edit", icon: "edit"},
            "cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "quit": {name: "Quit", icon: function($element, key, item){ return 'context-menu-icon context-menu-icon-quit'; }}
        }
    });

    $.contextMenu({
        selector: '.context-menu-leftclick',
        trigger: 'left',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        resize:true,
        items: {
            "edit": {name: "Edit", icon: "edit"},
            "cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "quit": {name: "Quit", icon: function($element, key, item){ return 'context-menu-icon context-menu-icon-quit'; }}
        }
    });

    $.contextMenu({
        selector: '.context-menu-toastr',
        callback: function(key, options) {
            var m = "clicked: " + key,
                o = {
                    "iconClass":"toast-just-text toast-primary",
                    "id":"toastr-primary"
                };
            toastr.warning(m,o);
        },
        resize:true,
        items: {
            "edit": {name: "Edit", icon: "edit"},
            "cut": {name: "Cut", icon: "cut"},
            "copy": {name: "Copy", icon: "copy"},
            "paste": {name: "Paste", icon: "paste"},
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "quit": {name: "Quit", icon: function(){
                return 'context-menu-icon context-menu-icon-quit';
            }}
        }
    });

    $.contextMenu({
        selector: '.context-menu-keeping',
        callback: function(key, options) {
            var m = "clicked: " + key;
            window.console && console.log(m) || alert(m);
        },
        items: {
            "edit": {
                name: "Closing on Click",
                icon: "edit",
                callback: function(){ return true; }
            },
            "cut": {
                name: "Open after Click",
                icon: "cut",
                callback: function(){ return false; }
            }
        }
    });

}(window, document, jQuery);