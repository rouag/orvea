(function ($) {
    "use strict";

    var $body = $("body");
    $.extend(CORE_TEMP.function, {
        SiteColor: function () {
            var $site_color = $('.site-color'), /* variable used on Site Color Settings */
                $site_color_elements = $('#site-color'),
                $site_dark_color_elements = $('#site-dark-color'),
                $site_dark_color_switch = $('.dark-color-switch'), /* variable used on Site Color Settings */
                $cssRoot = '../../..//smart_internal_portal/static/src/assets/layouts/layout-left-menu/css/color/'; /* variable used on Site CSS path */


            /*----- START SITE COLOR SETTINGS JS -----*/

            $site_color.children('div').on('click', function (e) {
                e.preventDefault();
                var $this = $(this), /* global variable */
                    $this_color = $this.attr('data-color'),
                $site_dark_color = localStorage.getItem("site_dark_color");
                /* Global Color Value */

                // Remove and ADD color active class
                $site_color.children('div').removeClass('color-active'),
                    $this.addClass('color-active');

                // Change CSS href
                $site_color_elements.attr("href", $cssRoot + "light/color-" + $this_color + ".min.css");

                if ($site_dark_color !== null && $site_dark_color !== "") {
                    if ($("#site-dark-color").length == 0) {
                        $site_color_elements.after('<link id="site-dark-color" rel="stylesheet" href="' + $cssRoot + 'dark/color-' + $this_color + '-' + $site_dark_color + '.min.css">');
                    } else {
                        $('#site-dark-color').attr('href', $cssRoot + 'dark/color-' + $this_color + '-' + $site_dark_color + '.min.css');
                    }
                }

                // Check Color value is null or not
                if ($this_color == null || $this_color == "") {
                    localStorage.setItem("site_color", $this_color);
                } else {
                    localStorage.setItem("site_color", $this_color);
                }

            });

            // Get Template Color from local storage
            if (localStorage.getItem("site_color") !== null) {
                $site_color.children('div[data-color=' + localStorage.getItem("site_color") + ']').trigger('click');
            }

            /*----- END SITE COLOR SETTINGS JS -----*/

            /*----- START SITE DARK COLOR SETTINGS JS -----*/

            $site_dark_color_switch.on('click', function () {
                // Check value true is true
                if ($(".site-dark-check").prop("checked") == true) {
                    $('.dark-color').css("font-weight", "700").html("Dark");
                    localStorage.setItem("site_dark_color", "gray");

                    // Get Template Color and dark color from local storage
                    var site_color = localStorage.getItem("site_color");
                    var site_dark_color = localStorage.getItem("site_dark_color");

                    if (site_dark_color !== null && site_dark_color !== "") {
                        if (site_color == null) {
                            $site_color_elements.after('<link id="site-dark-color" rel="stylesheet" href="' + $cssRoot + 'dark/color-default-' + site_dark_color + '.min.css">');
                        } else if ($("#site-dark-color").length == 0) {
                            $site_color_elements.after('<link id="site-dark-color" rel="stylesheet" href="' + $cssRoot + 'dark/color-' + site_color + '-' + site_dark_color + '.min.css">');
                        } else {
                            $('#site-dark-color').attr('href', $cssRoot + 'dark/color-' + site_color + '-' + site_dark_color + '.min.css');
                        }
                    } else {
                        $('#site-dark-color').remove();
                    }

                } else {
                    $('.dark-color').css("font-weight", "normal").html("Light");
                    localStorage.removeItem("site_dark_color");
                    $('#site-dark-color').remove();
                }
            });


            // Det Template Dark Color from local storage
            if (localStorage.getItem("site_dark_color") !== null) {
                $('.dark-color').css("font-weight", "700").html("Dark");
                $('.dark-color-switch').children('.js-switch').prop('checked', true);
                $site_dark_color_switch.trigger('click');
            }

            /*----- END SITE DARK COLOR SETTINGS JS -----*/
        },
        NavigetionLightDark : function(){
            var $nav_dark_color = $('.nav-color-switch'), /* variable used on Navigation Color Settings */
                $nav_dark_check = $('.nav-dark-check'),
                $nav_color = $('.nav-dark-color');
            $nav_dark_color.on('click', function (e) {
                e.preventDefault();
                if ($nav_dark_check.prop("checked") == true) {
                    $nav_color.css("font-weight", "700").html("Light");
                    localStorage.setItem("navigation_light", "light");
                    $body.addClass('nav-light');
                } else {
                    $nav_color.css("font-weight", "normal").html("Dark");
                    localStorage.removeItem("navigation_light");
                    $body.removeClass('nav-light');
                }

            });

            if (localStorage.getItem("navigation_light") !== null) {
                if ($nav_dark_check.prop("checked") != true) {
                    $nav_color.css("font-weight", "normal").html("Dark");
                }
                $nav_dark_color.children('.js-switch').prop('checked', true);
                $nav_dark_color.trigger('click');
            }
        },
        VerticalNavFixed: function(){
            /*----- START NAVIGATION OVERLAY SETTINGS JS -----*/
            var $nav_overlay = $('.nav-fixed-switch');

            $nav_overlay.on('click', function (e) {
                e.preventDefault();
                if ($(".nav-fixed-check").prop("checked") == true) {
                    $('.nav-fixed-text').css("font-weight", "700").html("overlay");
                    localStorage.setItem("navigation_type", "overlay");
                    $body.addClass('menu-overlay');
                    if($body.hasClass('nav-menu-icon')){
                        CORE_TEMP.function.initPerfectScroll($("#site-menu"));
                    }
                } else {
                    $('.nav-fixed-text').css("font-weight", "normal").html("fixed");
                    localStorage.removeItem("navigation_type");
                    $body.removeClass('menu-overlay');
                    if($body.hasClass('nav-menu-icon')){
                        CORE_TEMP.function.DestroyPerfectScroll($("#site-menu"));
                    }
                }
                $(window).trigger('resize');
            });

            if (localStorage.getItem("navigation_type") !== null) {
                if ($(".nav-fixed-check").prop("checked") != true) {
                    $('.nav-fixed-text').css("font-weight", "normal").html("fixed");
                }
                $nav_overlay.children('.js-switch').prop('checked', true);
                $nav_overlay.trigger('click');
            }

            /*----- END NAVIGATION OVERLAY SETTINGS JS -----*/
        },
        LeftMenuTogglebutton: function () {
            /*
             * nav-menu-icon: only for icon menu
             * nav-menu-hide: Hide Nav menu
             * nav-menu-clicked - Flag if menu is opened or closed
             *
             * */
            $('.left-menu-toggle').on('click', function (e) {
                e.preventDefault();
                var $body = $('body');
                if (!$body.hasClass('nav-menu-icon') && !$body.hasClass('nav-menu-hide')) {
                    // This part will execute while we are closing menu to ICON MENU.
                    if ($(window).width() < 768) {
                        $body.addClass('nav-menu-hide').addClass('nav-menu-clicked');
                    }
                    else {
                        $body.addClass('nav-menu-icon nav-menu-clicked').removeClass('nav-menu-hide');
                        $(this).children('i').removeClass('icon_menu toggle-icon').addClass('arrow_carrot-right toggle-left');
                        if (!$body.hasClass('menu-overlay')) {
                            CORE_TEMP.function.DestroyPerfectScroll($("#site-menu"));
                        }
                    }
                }
                else if ($body.hasClass('nav-menu-icon')) {
                    // This part will execute while we are opening menu to DESKTOP MENU.
                    CORE_TEMP.function.initPerfectScroll($("#site-menu"));
                    $body.removeClass('nav-menu-icon nav-menu-hide nav-menu-clicked');
                    $(this).children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                    if ($(window).width() < 992) {
                        $body.addClass('nav-menu-clicked');
                    }
                }
                else {
                    // This part will execute while we are hidding menu completely.
                    $body.removeClass('nav-menu-hide').addClass('nav-menu-clicked');
                    $(this).children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                    CORE_TEMP.function.initPerfectScroll($("#site-menu"));

                }
                CORE_TEMP.function.TriggerResize();
            });
            $('.right-menu-toggle').on('click', function (e) {
                e.preventDefault();
                var $body = $('body');
                $body.removeClass('nav-menu-icon').addClass('nav-menu-hide nav-menu-clicked');
                $('.left-menu-toggle').children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                CORE_TEMP.function.TriggerResize();
            });

        },
        Leftsidemenu: function () {
            $('.sidebar-menu .sub-item > a').on('click', function () {
                var $this = $(this).parent('li'),
                    $thisscroll = $this.parent('.sub-menu');
                if (!$body.hasClass('nav-menu-icon') || $body.hasClass('menu-overlay')) {
                    if ($this.has('ul')) {
                        if ($this.hasClass('active')) {
                            $this.removeClass('active');
                            $this.children('ul').removeClass('show-menu');
                            return;
                        }
                        $this.addClass('active');
                    }
                }
            });

        },
        NavigetionMenuActive: function () {
            if (!$body.hasClass('nav-menu-icon')) {
                var $pathArray = window.location.pathname.split("/").pop(),
                    $currentpageurl = $("a[href='" + $pathArray + "']");

                $currentpageurl.parent('li').addClass('active');
                if ($currentpageurl.parent('.sub-menu') && $currentpageurl.parent('.main-menu')) {
                    $currentpageurl.parents('li').addClass('active');
                }
            }
        },
        initLeftMenu: function () {
            var viewportWidth = $(window).width();
            var $body = $('body'),
                $lest_menu_toggle = $('.left-menu-toggle');
            if (viewportWidth < 992 && viewportWidth > 767) {
                if (!$body.hasClass('nav-menu-hide') && !$body.hasClass('nav-menu-clicked')) {
                    $body.addClass('nav-menu-icon');
                    $lest_menu_toggle.children('i').removeClass('icon_menu toggle-icon').addClass('arrow_carrot-right toggle-left');
                    CORE_TEMP.function.DestroyPerfectScroll($("#site-menu"));
                }
                else if ($body.hasClass('nav-menu-hide') && !$body.hasClass('nav-menu-clicked')) {
                    $body.addClass('nav-menu-icon').removeClass('nav-menu-hide');
                    $lest_menu_toggle.children('i').removeClass('icon_menu toggle-icon').addClass('arrow_carrot-right toggle-left');
                }
            }
            else if (viewportWidth < 768) {
                if(!$body.hasClass('nav-menu-hide') && !$body.hasClass('nav-menu-icon')){
                    CORE_TEMP.function.DestroyPerfectScroll($("#site-menu"));
                    CORE_TEMP.function.initPerfectScroll($("#site-menu"));
                }
                if (!$body.hasClass('nav-menu-hide') && !$body.hasClass('nav-menu-clicked')) {
                    $body.addClass('nav-menu-hide').removeClass('nav-menu-icon');
                    $lest_menu_toggle.children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                }
                else if ($body.hasClass('nav-menu-icon nav-menu-clicked')) {
                    $body.addClass('nav-menu-hide').removeClass('nav-menu-icon nav-menu-clicked');
                    $lest_menu_toggle.children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                }
            } else {
                if (!$body.hasClass('nav-menu-clicked')) {
                    $body.removeClass('nav-menu-hide nav-menu-icon');
                    $lest_menu_toggle.children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                }
            }
            if (viewportWidth > 991) {
                if ($body.hasClass('nav-menu-clicked') && !$body.hasClass('nav-menu-icon') && !$body.hasClass('nav-menu-hide')) {
                    $body.removeClass('nav-menu-clicked');
                    $lest_menu_toggle.children('i').removeClass('arrow_carrot-right toggle-left').addClass('icon_menu toggle-icon');
                }
            }
        },
        Loaderinit: function () {
            $body.addClass('loaded');
        }
    });
    $.extend(CORE_TEMP.onReady, {
        layoutOnReady: function () {
            CORE_TEMP.function.LeftMenuTogglebutton();
            CORE_TEMP.function.Leftsidemenu();
            CORE_TEMP.function.initLeftMenu();
            CORE_TEMP.function.SiteColor();
            CORE_TEMP.function.NavigetionLightDark();
            CORE_TEMP.function.VerticalNavFixed();
        }
    });
    $.extend(CORE_TEMP.onLoad, {
        layoutOnLoad: function () {
            CORE_TEMP.function.NavigetionMenuActive();
            CORE_TEMP.function.Loaderinit();
        }
    });
    $.extend(CORE_TEMP.onResize, {
        layoutOnResize: function () {
            CORE_TEMP.function.initLeftMenu();
        }
    });
})(jQuery);