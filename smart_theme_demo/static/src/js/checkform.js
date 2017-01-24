// <![CDATA[
function checkformload() { 
	$(".form-control").focus(function () {
		$(this).parent().removeClass('has-error');
	});
	/*	onblur	*/
	function btnCheckform() {
	    $('.form-horizontal').each(function () {
			var formId = $(this).attr('id');
	        $(this).find('.btn-primary').click(function () {
	            if (typeof formId !== typeof undefined && formId !== false) {

					var error = [];
	                var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;

	                $('[id$="' + formId + '"] input.required:not(:disabled), [id$="' + formId + '"] textarea.required').each(function () {
	                    var placeholder = $(this).attr('placeholder');
	                    if ($(this).val() == '') {
	                        error.push(placeholder + ' ضروري');
	                        $(this).parent().addClass('has-error');
	                    } else {
	                        if ($(this).hasClass('email')) {
	                            if (!reg.test($(this).val())) {
	                                error.push(placeholder + ' غير صحيح');
	                                $(this).parent().addClass('has-error');
	                            }
	                        }
	                    }
	                });
	                if($('[id$="' + formId + '"] input[type=checkbox]').length) {
						$('[id$="' + formId + '"] input[type=checkbox]').each(function () {
							if ($(this).is(':checked')) {
								jQuery(this).closest(".niceCheck").removeClass('has-error');
							}else{
								jQuery(this).closest(".niceCheck").addClass('has-error');
							error.push('Checkbox required');
							}
						});
	                }
	                $('[id$="' + formId + '"] select.form-control.required').each(function () {
	                    var placeholder = $(this).parent().prev('label').text();
	                    if ($(this).val() == '0') {
	                        error.push(placeholder + ' ضروري');
	                        $(this).parent().addClass('has-error');
	                    } else {
	                        $(this).parent().addClass('has-success');
	                        $(this).parent().removeClass('has-error');
	                    }
	                });

	                if (error.length > 0) {
	                    if (typeof console == 'object') console.log(error);
	                    return false;
	                }

	                if (error.length == 0) {
	                    $('[id$="' + formId + '"] .btn-primary').attr('rel', 'Go')
	                    return true;
	                }
	                return true;
	            }
	        });
	    });
	}

	$(document).ready(function () {
	
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

		/******************************************************************************************************************
									Fields Regex
		 ******************************************************************************************************************/
		if ($('.CivilRegistry').length > 0) {
			$('.CivilRegistry').attr('maxlength', '11').attr('minlength', '10');
			$('.CivilRegistry').bind("keypress", function (event) {
				if (event.charCode != 0 && event.charCode != 32) {
					var regex = new RegExp("^[0-9\+]+$");
					var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
					if (!regex.test(key)) {
						event.preventDefault();
						return false;
					}
				}
			});
		}

		//OnlyNbr
		if ($('.OnlyNbr').length > 0) {
			$('.OnlyNbr').focus(function () {$(this).tooltip({ 'trigger': 'focus', 'placement': 'top', 'title': 'أرقام فقط' }).tooltip('show');});
			$('.OnlyNbr').bind("keypress", function (event) {
				$(this).attr('maxlength', '15');
				if (event.charCode != 0 && event.charCode != 32) {
					var regex = new RegExp("^[0-9\+]+$");
					var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
					if (!regex.test(key)) {
						event.preventDefault();
						return false;
					}
				}
			});
		}
		
		//OnlyLatin
		if ($('.OnlyLatin').length > 0) {
			$(".OnlyLatin").focus(function () {$(this).tooltip({ 'trigger': 'focus', 'placement': 'top', 'title': 'الأحرف اللاتينية' }).tooltip('show');});
			$(".OnlyLatin").on("keypress", function(event) {
				var OnlyLatin = /[A-Za-z \-]/g;
				var key = String.fromCharCode(event.which);
				if (event.keyCode == 8 || event.keyCode == 37 || event.keyCode == 39 || OnlyLatin.test(key)) {
					return true;
				}
				return false;
			});
		}

		//OnlyArabic
		if ($('.OnlyArabic').length > 0) {
			$('.OnlyArabic').focus(function () {$(this).tooltip({ 'trigger': 'focus', 'placement': 'top', 'title': 'الأحرف العربية' }).tooltip('show');});
			$('.OnlyArabic').bind("keypress", function (event) {
				if (event.charCode != 0 && event.charCode != 32) {
					var regex = new RegExp("^[\u0600-\u06ff]|[\u0750-\u077f]|[\ufb50-\ufc3f]|[\ufe70-\ufefc]+$");
					var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
					if (!regex.test(key)) {
						event.preventDefault();
						return false;
					}
				}
			});
		}

		//	phone, mobile
		if ($('.phone, .mobile').length > 0) {
			$('.phone, .mobile').attr('maxlength', '10').attr('minlength', '10');
			$('.phone, .mobile').bind("keypress", function (event) {
				if (event.charCode != 0 && event.charCode != 32) {
					var regex = new RegExp("^[0-9\+]+$");
					var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
					if (!regex.test(key)) {
						event.preventDefault();
						return false;
					}
				}
			});
		}

		if ($('.zipCode').length > 0) {
			$('.zipCode').attr('maxlength', '5');
			$('.zipCode').bind("keypress", function (event) {
				if (event.charCode != 0 && event.charCode != 32) {
					var regex = new RegExp("^[0-9\+]+$");
					var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
					if (!regex.test(key)) {
						event.preventDefault();
						return false;
					}
				}
			});
		}

		if ($('div.calendar').length > 0) {
			var calendar = $.calendars.instance('ummalqura', 'ar');
			$('div.calendar input.form-control').each(function () {
				$(this).calendarsPicker({ calendar: calendar });
			});
			$('.calendar > i').click(function () {
				$(this).parent().find('input').focus();
			});
		}
		
		/******************************************************************************************************************
									textarea autoresize
		 ******************************************************************************************************************/
		if(jQuery('textarea[data-autoresize]').length > 0) {
			jQuery.each(jQuery('textarea[data-autoresize]'), function() {
				var offset = this.offsetHeight - this.clientHeight;
				var resizeTextarea = function(el) {
					jQuery(el).css('height', 'auto').css('height', el.scrollHeight + offset);
				};
				jQuery(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
			});
		}
		
		/******************************************************************************************************************
									radio / checkbox
		 ******************************************************************************************************************/
		if(jQuery('input:radio').length > 0) {
			$('input:radio').each(function () {
				var count2 = $(this).parent().children().length;
				if (count2 > 1) { $(this).parent().addClass('radio'); } else { $(this).parents('table').addClass('radio-inline'); }
			});
		}
		if(jQuery('input:checkbox').length > 0) {
			$('input:checkbox').each(function () {
				var count2 = $(this).parent().children().length;
				if (count2 > 1) { $(this).parent().addClass('checkbox'); } else { $(this).parents('table').addClass('checkbox-inline'); }
			});
		}
	});
}

checkformload();
// ]]>