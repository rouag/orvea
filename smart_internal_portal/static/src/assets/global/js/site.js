var CORE_TEMP = CORE_TEMP || {};

/*function resize() {
 }*/

$().extend('resize', {
    init: function() {

    }
});
!(function ($) {
    "use strict";
    CORE_TEMP.function = {
        SiteSettings: function () {
            var $righttoggle = $('.icon-right');
            $righttoggle.on('click', function () {
                $body.toggleClass("site-settings");
            });
        },
        PerfectScroll: function () {
            if ($().perfectScrollbar) {
                $('[data-plugin="custom-scroll"]').each(function () {
                    CORE_TEMP.function.initPerfectScroll($(this));
                });
            }
        },
        initPerfectScroll: function (element) {
            if ($().perfectScrollbar) {
                var $this = element,
                    $width,
                    $height,
                    $options = $.extend({}, $this.data());
                if (!$options.height) {
                    $height = "250px";
                } else {
                    $height = $options.height;
                }
                if ($options.min) {
                    var minwidth = $options.min;
                }
                $width = $options.width;
                var scrollwidth = $width;
                var scrollheight = $height;
                //$options.suppressScrollX = true;
                $this.height(scrollheight);
                $this.children('div').css({"min-width": minwidth, "width": "100%"});
                $this.perfectScrollbar($options);
            }
        },
        DestroyPerfectScroll: function (element) {
            if ($().perfectScrollbar) {
                element.perfectScrollbar('destroy');
            }
        },
        SimpleMEditor: function () {
            if (typeof SimpleMDE !== 'undefined') {
                $('[data-plugin="simplemarkdown"]').each(function () {
                    var $this = $(this),
                        $options = $.extend({}, $this.data());
                    $options.element = document.getElementById($this.attr('id'));
                    new SimpleMDE($options);
                });
            }
        },
        toastr: function () {
            if (typeof toastr !== 'undefined') {
                $('[data-plugin="toastr"]').on("click", function (e) {
                    e.preventDefault();
                    var $this = $(this),
                        options = $.extend(!0, {}, $this.data()),
                        message = options.message,
                        type = options.type,
                        title = options.title;
                    if (!message) {
                        message = "";
                    }
                    if (!type) {
                        type = "info";
                    }
                    if (!title) {
                        title = "";
                    }
                    switch (type) {
                        case "success":
                            toastr.success(message, title, options);
                            break;
                        case "warning":
                            toastr.warning(message, title, options);
                            break;
                        case "error":
                            toastr.error(message, title, options);
                            break;
                        case "info":
                            toastr.info(message, title, options);
                            break;
                        default:
                            toastr.info(message, title, options)
                    }
                })
            }
        },
        amaran: function () {
            $('[data-plugin="amaran"]').on('click', function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $.amaran($options);
            });
        },
        updateScrollbars: function (e) {
            $('[data-plugin="custom-scroll"]').perfectScrollbar('update');
        },
        Swithery: function () {
            if ("undefined" != typeof Switchery) {
                var $color = $('.site-color').find('.color-active').data('color-code');
                var defaults = {color: $color};

                $('[data-plugin="switchery"]').each(function () {
                    var $this = $(this),
                        $options = $.extend({}, defaults, $this.data());
                    new Switchery(this, $options);
                });
            }
        },
        Checkall: function () {
            $(".check_all").on('change', function (e) {
                var $this = $(this);
                if ($this.is(':checked') === true) {
                    $this.parents('div.right_sidebar_contain').find('[type="checkbox"]').prop('checked', true);
                }
                else {
                    $this.parents('div.right_sidebar_contain').find('[type="checkbox"]').prop('checked', false);
                }
            });
            $('.mail_message .checkbox-squared').find('[type="checkbox"]').change(function () {
                $('.mail_message').find('[type="checkbox"]').length == $('.mail_message').find('[type="checkbox"]:checked').length ? $(".check_all").prop('checked', true) : $(".check_all").prop('checked', false);
            });
        },
        FullScreen: function () {
            if (typeof screenfull !== 'undefined') {
                $('[data-plugin="fullscreen"]').on("click", function () {
                    screenfull.toggle();
                });
            }
        },
        Dropopen: function () {
            $('[data-open="true"]').on("click", function () {
                var $this = $(this);
                var $checkvalue = $this.parent().children('.dropdown-menu');
                if (!$checkvalue.hasClass("show")) {
                    $('.dropdown-menu').removeClass('show');
                }
                $checkvalue.toggleClass('show');
            });
            $body.mouseup(function () {
                if ($('[data-open="true"]').parent().children('.dropdown-menu').hasClass("show")) {
                    $('[data-open="true"]').parent().children('.dropdown-menu').removeClass('show');
                }
            });
            $('[data-open="true"]').parent().mouseup(function () {
                return false;
            });
        },
        //Panel Jquery
        PanelFullscreen: function () {
            $('[data-toggle="panel-full"]').on('click', function () {
                var $this = $(this),
                    $panel = $this.closest('.content');
                $panel.toggleClass('showFullscreen');
                screenfull.toggle($panel[0]);
                if ($panel.hasClass('showFullscreen')) {
                    $this.children('i').removeClass('arrow_expand').addClass('arrow_condense');
                } else {
                    $this.children('i').removeClass('arrow_condense').addClass('arrow_expand');
                }
            });
        },
        PanelCollapse: function () {
            $('[data-toggle="panel-collapse"]').on('click', function () {
                var $this = $(this),
                    $panel = $this.closest('.content');
                if (!$panel.hasClass('collapse')) {
                    $panel.addClass('collapse');
                    $this.children('span').removeClass('icon_minus-06').addClass('icon_plus');
                } else {
                    $this.children('span').removeClass('icon_plus').addClass('icon_minus-06');
                    $panel.removeClass('collapse');
                }
            });
        },
        PanelClose: function () {
            $('[data-toggle="panel-close"]').on('click', function () {
                var $this = $(this),
                    $panel = $this.closest('.content');
                if (!$panel.hasClass('panel-close')) {
                    $panel.addClass('panel-close');
                }
            });
        },
        PanelRefresh: function () {
            $('[data-toggle="panel-refresh"]').on('click', function () {
                var $this = $(this),
                    $panel = $this.closest('.content');
                var $loading = $('<div class="mod model-1"><div class="spinner"></div></div>');
                $panel.addClass('loading-panel');
                $panel.prepend($loading);
                setTimeout(function () {
                    $loading.remove();
                    $panel.removeClass('loading-panel');
                }, 3000);
            });
        },
        DropdownNiceSelect: function () {
            $('[data-plugin="niceselect"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.niceSelect(this, $options);
            });
        },
        Dropdowncheckbox: function () {
            $('[data-plugin="multiselect"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.multiselect(this, $options);
            });
        },
        Progressbar: function () {
            $('[data-plugin="progressbar"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data()),
                    $protype = $options.type,
                    $animate = $options.animate;
                if ($protype == "Circle") {
                    $this = new ProgressBar.Circle("#" + $this.attr('id'), $options);
                }
                else if ($protype == "Line") {
                    $this = new ProgressBar.Line("#" + $this.attr('id'), $options);
                }
                $this.animate($animate);
            });
        },
        BootstrapTooltip: function () {
            $('[data-toggle="tooltip"]').tooltip();
        },
        PowerTip: function () {
            if ("undefined" != typeof powerTip) {
                $('[data-toggle="powertip"]').each(function () {
                    var $this = $(this),
                        $options = $.extend({}, $this.data());
                    $this.powerTip($options);
                });
            }
        },
        PopoverToggle: function () {
            $('[data-toggle="popover"]').popover();
        },
        Toolbar: function () {
            if ("undefined" != typeof toolbar) {
                $('[data-plugin="toolbar"]').each(function () {
                    var $this = $(this),
                        $options = $.extend({}, $this.data());
                    $this.toolbar($options);
                });
            }
        },
        Sortable: function () {
            $('[data-plugin="sortable"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                Sortable.create(this, $options);
            });
        },
        Nestable: function () {
            $('[data-plugin="nestable"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.nestable($options);
            });
        },
        Dropify: function () {
            $('[data-plugin="dropify"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.dropify($options);
            });
        },
        editable: function () {
            $('[data-plugin="editable"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.editableTableWidget($options);
            });
        },
        numericInput: function () {
            $('[data-count="numeric"]').each(function () {
                var $this = $(this);
                $this.numericInputExample();
            });
        },
        Footable: function () {
            $('[data-plugin="footable"]').each(function () {
                var $this = $(this);
                $this.footable();
            });
        },
        Datatable: function () {
            $('[data-plugin="datatable"]').each(function () {
                var $this = $(this),
                    $defaults = {
                        "oLanguage": {
                            "oPaginate": {
                                "sFirst": "<", // This is the link to the first page
                                "sPrevious": "«", // This is the link to the previous page
                                "sNext": "»", // This is the link to the next page
                                "sLast": ">" // This is the link to the last page
                            }
                        }
                    },
                    $options = $.extend({}, $defaults, $this.data());
                $this.DataTable($options);
            });
        },

        Wizard: function () {
            $('[data-plugin="smartwizard"]').each(function () {
                var $this = $(this),
                    $callback = $this.data("callback"),
                    $defaults = {keyNavigation: false},
                    $options = $.extend({}, $defaults, $this.data());
                if ($callback) {
                    $options.onFinish = onFinishCallback;
                }
                $this.smartWizard($options);
            });

            function onFinishCallback() {
                alert('Finish Called');
            }
        },
        Counter: function () {
            $('[data-plugin="counter"]').each(function () {
                var $this = $(this);
                $this.counterUp();
            });
        },
        Slick: function () {
            $('[data-plugin="slick"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.slick($options);
            });
        },
        Lightbox: function () {
            $('[data-plugin="lightbox"]').each(function () {
                var $this = $(this),
                    $atag = $this.find('a');
                $atag.simpleLightbox();
            });
        },
        Collapse: function () {
            $('[data-widget="collapse"]').on('click', function () {
                var $this = $(this);
                $this.closest(".content").find(".icon_minus-06").toggleClass("icon_plus");
                $this.closest(".content").find(".dashboard-box").slideToggle(500);
            });
        },
        Close: function () {
            $('[data-widget="close"]').on('click', function () {
                var $this = $(this);
                $this.closest(".content").hide();
            });
        },
        Tudo: function () {
            $('[data-list="tudo"]').on("change", function () {
                "use strict";
                var $this = $(this),
                    $checkbox = $this.find('[type="checkbox"]');
                $checkbox.is(":checked") ? $this.addClass("todo_completed") : $this.removeClass("todo_completed");
                var $total = $('.todo_completed').length,
                    $totaltodulist = $('.todo_remaining').html(),
                    $finaltodutotal = $totaltodulist - $total;
                $('.todo_total').html($finaltodutotal);
            }), $('[data-list="tudo"]').trigger("change");
        },
        resize: function () {
            if (document.createEvent) {
                var ev = document.createEvent('Event');
                ev.initEvent('resize', true, true);
                window.dispatchEvent(ev);
            } else {
                element = document.documentElement;
                var event = document.createEventObject();
                element.fireEvent("resize", event);
            }
        },
        Cookie: function () {
            $('[data-plugin="cookie"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.cookieBar($options);
            });
        },
        siteSerchBox: function () {
            var $clonediv_overlay = $(".search-overlay"),
                $clonediv = $(".searchbox"),
                $search_close = $(".search_close");
            $clonediv.on('click', function () {
                var $this = $(this);
                $this.toggleClass('search-open');
                $clonediv_overlay.toggleClass('search-active');
            });

            $search_close.on('click', function () {
                $clonediv_overlay.removeClass('search-active');
                $('.search_input').val('');
            });

            if (!String.prototype.trim) {
                (function() {
                    // Make sure we trim BOM and NBSP
                    var rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;
                    String.prototype.trim = function() {
                        return this.replace(rtrim, '');
                    };
                })();
            }

            [].slice.call( document.querySelectorAll( 'input.search_input' ) ).forEach( function( inputEl ) {
                // in case the input is already filled..
                if( inputEl.value.trim() !== '' ) {
                    classie.add( inputEl.parentNode, 'input-focued' );
                }

                // events:
                inputEl.addEventListener( 'focus', onInputFocus );
                inputEl.addEventListener( 'blur', onInputBlur );
            } );

            function onInputFocus( ev ) {
                classie.add( ev.target.parentNode, 'input-focued' );
            }

            function onInputBlur( ev ) {
                if( ev.target.value.trim() === '' ) {
                    classie.remove( ev.target.parentNode, 'input-focued' );
                }
            }

        },
        Flatpickr: function () {
            $('[data-plugin="flatpickr"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.flatpickr($options);
            });
        },
        TriggerResize: function() {
            if (document.createEvent) {
                var ev = document.createEvent('Event');
                ev.initEvent('resize', true, true);
                window.dispatchEvent(ev);
            } else {
                element = document.documentElement;
                var event = document.createEventObject();
                element.fireEvent("onresize", event);
            }
        },
        magnificPopup: function() {
            $('[data-plugin="magnificPopup"]').each(function () {
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.magnificPopup($options);
            });
        },
        WavesEffects: function() {
            if (typeof Waves !== 'undefined') {
                Waves.attach('.flat-buttons', ['waves-button']);
                Waves.attach('.float-buttons', ['waves-button', 'waves-float']);
                Waves.attach('.float-button-light', ['waves-button', 'waves-float', 'waves-light']);
                Waves.attach('.flat-icon', ['waves-circle']);
                Waves.attach('.float-icon', ['waves-circle', 'waves-float']);
                Waves.attach('.float-icon-light', ['waves-circle', 'waves-float', 'waves-light']);
                Waves.init();
            }
        },
        NavigetionSearchMenu: function () {
            $.extend($.expr[":"], {
                "Contains": function(elem, i, match, array) {
                    return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
                }
            });
            var $menusearch = $("#live-search-box");
            $menusearch.on('change',function(){
                var $this = $(this).val();
                if ($this) {
                    $('.menu-title').hide();
                    $('.live-search-list').find("li a:not(:Contains(" + $this + "))").hide().parent().hide();
                    var $filter = $('.live-search-list').find("li a:Contains(" + $this + ")");
                    $filter.parent().hasClass("sub-item") ? ($filter.show().parents("li").show().addClass("open").closest("li").children("a").show().children("li").show(), $filter.siblings("ul").length > 0 && $filter.siblings("ul").children("li").show().children("a").show()) : $filter.show().parents("li").show().addClass("open").closest("li").children("a").show();
                }else{
                    $('.menu-title').show();
                    $('.live-search-list').find("li a").show().parent().show().removeClass("open");
                }
            }).keyup(function() {
                    $(this).change()
            });
        },
        JqueryKnob: function () {
            $('[data-plugin="jknob"]').each(function(){
                var $this = $(this),
                    $options = $.extend({}, $this.data());
                $this.knob($options);
            });
        },
        JqueryNewsTicker: function () {
			$('#news').newsTicker({
				row_height: 30,
				max_rows: 1,
				speed: 300,
				duration: 6000,
				prevButton: $('#nt-prev'),
				nextButton: $('#nt-next')
			});
        }
    };
    CORE_TEMP.onReady = {
        init: function () {
            CORE_TEMP.function.SiteSettings();
            CORE_TEMP.function.FullScreen();
            CORE_TEMP.function.Dropopen();
            CORE_TEMP.function.Checkall();
            CORE_TEMP.function.PanelFullscreen();
            CORE_TEMP.function.PanelCollapse();
            CORE_TEMP.function.PanelClose();
            CORE_TEMP.function.PanelRefresh();
            CORE_TEMP.function.DropdownNiceSelect();
            CORE_TEMP.function.Dropdowncheckbox();
            CORE_TEMP.function.SimpleMEditor();
            CORE_TEMP.function.Progressbar();
            CORE_TEMP.function.BootstrapTooltip();
            CORE_TEMP.function.PowerTip();
            CORE_TEMP.function.PopoverToggle();
            CORE_TEMP.function.Toolbar();
            CORE_TEMP.function.toastr();
            CORE_TEMP.function.amaran();
            CORE_TEMP.function.Sortable();
            CORE_TEMP.function.Nestable();
            CORE_TEMP.function.Dropify();
            CORE_TEMP.function.editable();
            CORE_TEMP.function.numericInput();
            CORE_TEMP.function.Footable();
            CORE_TEMP.function.Datatable();
            CORE_TEMP.function.Wizard();
            CORE_TEMP.function.Counter();
            CORE_TEMP.function.Slick();
            CORE_TEMP.function.Lightbox();
            CORE_TEMP.function.Collapse();
            CORE_TEMP.function.Close();
            CORE_TEMP.function.Tudo();
            CORE_TEMP.function.Cookie();
            CORE_TEMP.function.siteSerchBox();
            CORE_TEMP.function.Flatpickr();
            CORE_TEMP.function.magnificPopup();
            CORE_TEMP.function.WavesEffects();
            CORE_TEMP.function.NavigetionSearchMenu();
            CORE_TEMP.function.JqueryKnob();
            CORE_TEMP.function.JqueryNewsTicker();
        }
    };

    CORE_TEMP.onLoad = {
        init: function () {
            CORE_TEMP.function.PerfectScroll();
            CORE_TEMP.function.updateScrollbars();
            CORE_TEMP.function.Swithery();
        }
    };

    CORE_TEMP.onResize = {
        init: function () {
            CORE_TEMP.function.updateScrollbars();
        }
    };

    var $window = $(window),
        $windowheight = $(window).height(),
        $body = $('body');
    $(document).on('ready', function () {
        for (var init in CORE_TEMP.onReady) {
            CORE_TEMP.onReady[init]();
        }
    });
    $window.on('load', function () {
        for (var init in CORE_TEMP.onLoad) {
            CORE_TEMP.onLoad[init]();
        }
    });
    $window.on('resize', function () {
        for (var init in CORE_TEMP.onResize) {
            CORE_TEMP.onResize[init]();
        }
    });
})(jQuery);