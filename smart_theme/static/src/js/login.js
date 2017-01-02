// <![CDATA[
var windowW = window.innerWidth;
var windowH = window.innerHeight;
jQuery( window ).resize(function() {
	var windowW = window.innerWidth;
	var windowH = window.innerHeight;
	loginCenter();
});
jQuery(window).load(function() {});

jQuery(window).scroll(function (event) {
	
});
jQuery(document).ready(function () {
	loginCenter();

	jQuery('.checkbox').each(function(){
		var inputC = jQuery(this).find('input'),
			iconC  = jQuery(this).find('span i');
		if (inputC.is(':checked')) {iconC.show();}
		jQuery(this).find('label').click(function(){
			if (inputC.is(':checked')) {
				iconC.show('fast');
			}else{
				iconC.hide();
			}
		});
    });

	jQuery('#loginBox a').not('.newReg').click(function(){
		jQuery('#loginBox').fadeToggle('slow', function(){
			jQuery('#forgotPsswdBox').fadeToggle('fast');
		});
	});
	jQuery('#forgotPsswdBox a').click(function(){
		jQuery('#loginForm .has-error .form-control').parent().removeClass('has-success').removeClass('has-error');
		jQuery('#forgotPsswdBox').fadeToggle('slow', function(){
			jQuery('#loginBox').fadeToggle('fast');
		});
	});
	
	function runScript(e) {
	    if (e.keyCode == 13) {
	    	document.getElementById("loginform").submit();
	        return false;
	    }
	}

    /**************************************************************************************************************
                        Form all .form-control
    **************************************************************************************************************/
    if (jQuery('.form-control').length > 0) { // if nav-right Exist
        jQuery('.form-control').each(function () {
            var target = jQuery(this).attr("placeholder");
            jQuery(this).focus(function () {
                jQuery(this).attr("placeholder", "");
            });
            jQuery(this).blur(function () {
                jQuery(this).attr("placeholder", target);
            });
        });
        jQuery('select.form-control').each(function () {
            jQuery(this).select2();
        });
    }
	
		
	/******************************************************************************************************************
								SendPetition form
	 ******************************************************************************************************************/
	jQuery('.btn').click(function() {
		var attrId = jQuery(this).parent().attr('id');
			attrId = attrId.replace('Form', '');
		if (typeof attrId !== typeof undefined && attrId !== false) {
			var	btn = attrId.replace("btn", "");
		
			var error = [];
			var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
			
			jQuery('[id$="'+btn+'"] input.required, [id$="'+btn+'"] textarea.required').each(function () {
				var placeholder = jQuery(this).attr('placeholder');
				if(jQuery(this).val() == ''){
					error.push(placeholder + ' is required');
					jQuery(this).parent().addClass('has-error');
				}else{
					if(jQuery(this).hasClass('email')){
						if(!reg.test(jQuery(this).val())){
							error.push(placeholder + ' email is invalid');
							jQuery(this).parent().addClass('has-error');
						}
					}
				}
			});

			if (error.length > 0) {
				if ( typeof console == 'object' )console.log(error);
				return false;
			}

			if (error.length == 0) {
				return true;
			}

			return true;
		
		}
	});
});
/*===========================================================================================================================================
								Function
  ===========================================================================================================================================*/
function loginCenter(){
	var loginH = jQuery('#login').height();
	var centered = (windowH-loginH)/2;
	if(windowH > loginH){
		jQuery('#login').css({
			'margin-top' : centered+'px'
		})
	}else{
		jQuery('#login').removeAttr('style');
	}
}
// ]]>