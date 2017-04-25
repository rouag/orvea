!function (document, window, $) {
    "use strict";

    var croppicContainerDefaultOptions = {
        uploadUrl:'img_save_to_file.php',
        cropUrl:'img_crop_to_file.php',
        imgEyecandy:false,
    };
    var cropContainerDefault = new Croppic('cropContainerDefault', croppicContainerDefaultOptions);

    var croppicContainerLoaderOptions = {
        uploadUrl:'img_save_to_file.php',
        cropUrl:'img_crop_to_file.php',
        imgEyecandy:false,
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> '
    }

    var cropContainerLoasder = new Croppic('cropContainerLoasder', croppicContainerLoaderOptions);

    var croppicContaineroutputMinimal = {
        uploadUrl:'img_save_to_file.php',
        cropUrl:'img_crop_to_file.php',
        modal:false,
        doubleZoomControls:false,
        rotateControls: false,
        imgEyecandy:false,
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> ',
    }
    var cropContainerMinimal = new Croppic('cropContainerMinimal', croppicContaineroutputMinimal);

    var croppicContainerPreloadOptions = {
        uploadUrl:'img_save_to_file.php',
        cropUrl:'img_crop_to_file.php',
        loadPicture:'../../..//smart_internal_portal/static/src/assets/global/image/img_800x450.png',
        enableMousescroll:true,
        imgEyecandy:false,
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> ',
    }
    var cropContainerPreload = new Croppic('cropContainerPreload', croppicContainerPreloadOptions);

    var croppicContainerModalOptions = {
        uploadUrl:'img_save_to_file.php',
        cropUrl:'img_crop_to_file.php',
        modal:true,
        imgEyecandy:false,
        loaderHtml:'<div class="loader bubblingG"><span id="bubblingG_1"></span><span id="bubblingG_2"></span><span id="bubblingG_3"></span></div> ',
    }
    var cropContainerModal = new Croppic('cropContainerModal', croppicContainerModalOptions);


    var resizeEnd;
    $(window).on('resize', function() {
        clearTimeout(resizeEnd);
        resizeEnd = setTimeout(function() {
            $(window).trigger('resize-end');
        }, 1000);
    });

    $(window).on('resize-end', function() {
        cropContainerDefault.reset();
        cropContainerLoasder.reset();
        cropContainerMinimal.reset();
        cropContainerPreload.reset();
        cropContainerModal.reset();
    });


}(document, window, jQuery);
