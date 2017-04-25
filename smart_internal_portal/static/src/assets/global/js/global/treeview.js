!function (document, window, $) {
    "use strict";
    $('#basicTree').jstree({
        'core' : {
            'themes' : {
                'responsive': false
            }
        },
        'types' : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        'plugins' : ['types']
    });
    $('#checkboxtree').jstree({
        'core' : {
            'check_callback' : true,
            'themes' : {
                'responsive': false
            }
        },
        'types' : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        'plugins' : ['types', 'checkbox']
    });
    $('#dragAnddrop').jstree({
        'core' : {
            'check_callback' : true,
            'themes' : {
                'responsive': false
            }
        },
        'types' : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        'plugins' : ['types', 'dnd']
    });
    $('#ajaxdata').jstree({
        'core' : {
            'check_callback' : true,
            'themes' : {
                'responsive': false
            },
            'data' : {
                'url' : function (node) {
                    return node.id === '#' ? '../../..//smart_internal_portal/static/src/assets/data/root.json' : '../../..//smart_internal_portal/static/src/assets/data/root_child.json';
                },
                'data' : function (node) {
                    return { 'id' : node.id };
                }
            }
        },
        "types" : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        "plugins" : [ "contextmenu", "dnd", "search", "state", "types", "wholerow" ]
    });
    $('#searchTree').jstree({
        'core' : {
            'check_callback' : true,
            'themes' : {
                'responsive': false
            }
        },
        'types' : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        "plugins" : ["types","search"]
    });
    $('#contextmenuTree').jstree({
        'core' : {
            'check_callback' : true,
            'themes' : {
                'responsive': false
            }
        },
        'types' : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        "plugins" : ["types","contextmenu"]
    });
    $("#searchtreeform").submit(function(e) {
        e.preventDefault();
        $("#searchTree").jstree(true).search($("#searchvalue").val());
    });
    $('#ExpandCollapse').jstree({
        'core' : {
            'themes' : {
                'responsive': false
            }
        },
        'types' : {
            'default' : {
                'icon' : 'icon_folder'
            },
            'file' : {
                'icon' : 'icon_document'
            }
        },
        'plugins' : ['types']
    });
    $("#expand-all").on('click',function(e) {
        var $treeview = $("#ExpandCollapse");
        $treeview.jstree('open_all');
    });
    $("#collapse-all").on('click',function(e) {
        var $treeview = $("#ExpandCollapse");
        $treeview.jstree('close_all');
    });
}(document, window, jQuery);
