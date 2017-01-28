// <![CDATA[
function mainload() {
	var windowW = window.innerWidth;
	var windowH = window.innerHeight;
	jQuery( window ).resize(function() {
		var windowW = window.innerWidth;
		var windowH = window.innerHeight;
		setTimeout(function() { //location.reload();

		}, 500);
	});

	jQuery(window).load(function() {});
	
	jQuery(window).scroll(function (event) {});

	jQuery(document).ready(function () {


	    /*====================================================================================================
                                marking up
          ====================================================================================================*/
		/*	#connexion :  Close dropdown-menu*/
		$("body").mouseup(function (e) {
			var connexion = $("#connexion");
			if (e.target.id != connexion.attr('id') && !connexion.has(e.target).length) {
				jQuery('#connexion .dropdown').removeClass('open');
				jQuery('#connexion .dropdown > ul').removeAttr('style');
			}
		});
		
		if (jQuery('.dropdown-toggle').length > 0) {
			jQuery('.dropdown-toggle').click(function () {
				if (jQuery(this).parent().hasClass('open')) {
					jQuery(this).parent().find('ul').slideUp(function () {
						jQuery(this).parent().removeClass('open');
						jQuery(this).removeAttr('style');
					});
				} else {
					jQuery(this).parent().siblings().find('ul.dropdown-menu').slideUp();
					jQuery(this).parent().find('ul').slideToggle(function () {
						jQuery(this).parent().siblings().removeClass('open');
						jQuery(this).parent().addClass('open');
					});
				}
			});
			jQuery('.navbar-toggle').click(function () {
				jQuery('#mainMenu > ul').slideToggle();
			});
			
			// Add Active Class to current page
			var pathname = window.location.pathname;
			var page = pathname.split('/').pop();
            if (jQuery("#mainMenu .list-unstyled > li").length > 1) {jQuery("#mainMenu li").removeClass('open');}
			jQuery("#mainMenu li a").each(function () {
                var href = jQuery(this).attr('href');
                var sHref = href.split('/').pop();
                var rHref = href; //.replace('", false, true))', '');
                if (rHref == page) {
                    if (jQuery("#mainMenu .list-unstyled > li").length > 1) {jQuery(this).parents('.dropdown').addClass('open'); }
                    jQuery(this).parent().addClass('active');
                }
            });
		}

		// Avatar check loading // #welcomeMenuBox || #connexion
		$("#connexion img.img-responsive").each(function (index) {
			$(this)
				.load(function () {
					//console.log("Avatar image loaded correctly");
				})
				.error(function () {
					//console.log("error loading image");
					$(this).attr('src', '/_layouts/15/SEPM.WEB/assets/img/users/employee.png');
				});
		});

		/**************************************************************************************************************
							btnCheckform
		**************************************************************************************************************/
		if ($('.form-horizontal').length && !$('#coverflow').length) { 
			btnCheckform();
		}
		
		/**************************************************************************************************************
							btnTooltip
		**************************************************************************************************************/
		if (jQuery('.btnTooltip').length > 0) { // if insitTooltip Exist
			jQuery('.btnTooltip').tooltip({animated: 'fade'});
		}
		$('a').each(function () {
		    if ($(this).attr('title') != '') {
		        if ($(this).hasClass('ms-core-menu-root') || jQuery(this).closest(".topIcons2").length) { var Placement = 'right'; } else { var Placement = 'top'; }
		        $(this).tooltip({ animated: 'fade', placement: Placement });
		    }
		});

		/**************************************************************************************************************
							.newsticker
		**************************************************************************************************************/
		if ($('.newsticker').length > 0) { // if News ticker Exist
			$('.newsticker').newsTicker({
				row_height: 45,
				max_rows: 1,
				speed: 600,
				direction: 'up',
				duration: 4000,
				autostart: 1,
				pauseOnHover: 0
			});
		}

		/**************************************************************************************************************
							.addComments
		**************************************************************************************************************/
		// Add comment
		jQuery('.addComments').click(function(){
			jQuery("#comments-forms .form-control").val('');
			jQuery('#comments-forms').slideToggle();
		});
		jQuery('.replyComment a').click(function(){
			jQuery(".item .form-control").val('');
			jQuery(this).closest( ".item" ).siblings().find('.comment-reply').slideUp();
			jQuery(this).closest( ".item" ).find('.comment-reply').slideToggle(function(){});
		});

		/**************************************************************************************************************
							.filter
		**************************************************************************************************************/
		if (jQuery('.results-details').length > 0) {
			jQuery('.results-details > .lines > div').not('.details').click(function () {
				jQuery(this).closest(".lines").siblings().find('.details').slideUp();
				jQuery(this).closest(".lines").find('.details').slideToggle();
			});
		}
		
		/**************************************************************************************************************
							.scrollbox
		**************************************************************************************************************/
		if (jQuery('.scrollbox').length > 0) {
			jQuery('.scrollbox').perfectScrollbar();
		}
		
		/*************************************************************************************************************************************
												owlCarousel	 : lastEvents
		 *************************************************************************************************************************************/
		//blockNews
		if($("#lastEvents .owl-carousel").length){
			jQuery("#lastEvents .owl-carousel").each(function(){
				jQuery(this).owlCarousel({
					autoPlay : true, slideSpeed : 300, paginationSpeed : 400, singleItem:true, transitionStyle : "backSlide",items : 1,
					pagination : true,navigation : false//,navigationText: ["<i class='icon35-right'></i>","<i class='icon35-left'></i>"]
				});
			});
		}
		/**************************************************************************************************************
							moreDetails
		**************************************************************************************************************/
		if (jQuery('.moreDetails').length > 0) {
			jQuery(".moreDetails").each(function () {
				jQuery(this).click(function () {
					if(jQuery(this).closest('.lines').hasClass('open')){
						jQuery('.results .lines').removeClass('open').removeClass('disable');
						jQuery('.results .lines div.details').slideUp();
					}else{
						$(this).closest('.lines').siblings().removeClass('open').addClass('disable').find('div.details').slideUp();
						$(this).closest('.lines').removeClass('disable').find('div.details').slideDown( "slow", function() {
							jQuery(this).closest('.lines').toggleClass('open');
						});
					}
				});
				$(document).mouseup(function (e){
					var container = $(".moreDetails").closest('.lines');

					if (!container.is(e.target) // if the target of the click isn't the container...
						&& container.has(e.target).length === 0) // ... nor a descendant of the container
					{
						jQuery('.results .lines').removeClass('open').removeClass('disable');
						jQuery('.results .lines div.details').slideUp();
					}
				});
			});
		}

		/***********************************************************************************************************
								confirmModal
		 ***********************************************************************************************************/
		if (jQuery('#confirmModal').length > 0) {
			jQuery('.results .btn').each(function(){
				$(this).click(function(){
					var target = jQuery(this);
					var actionTxt	= $(this).text();
					if($(this).hasClass('btn-success')){var actionRef	= 1;}else{var actionRef	= 2;} // OK = 1 || No = 2 -->

					// Titles Modal form current Lines
					var LineTitle = $(this).closest('.lines').find('.modalLineTitle').text();
					if($('.filter').length){
						var FilterTitle = $(this).closest('.filter').find('.modalFilterTitle').text();
						var modalTitle = FilterTitle + ' - ' + LineTitle;
					}else{
						var modalTitle = LineTitle;
					}
					
					// attr data helper
					var dataKey = new Array(), dataValue = new Array();
					arr = $(this).closest('.lines').data();
					for(el in arr){;
						dataKey.push(el);
						dataValue.push(arr[el]);
					}
					if (typeof console == 'object') console.log(dataKey);
					if (typeof console == 'object') console.log(dataValue);
					$(this).attr('data-toggle', 'modal').attr('data-target' , '#confirmModal').attr('data-backdrop' , 'static').attr('data-keyboard' , 'false');
					
					// btn remove all siblings class active
					jQuery(this).closest(".lines").find('.btn').not(this).removeClass('active');
					
					// btn toggleClass active && luanche 
					$( this ).toggleClass(function() {
					  if ( $( this ).is( ".btn" ) ) {
						$("#confirmModal").on('show.bs.modal', function (event) {
							var modal	= $(this);

							modal.find('.modal-title').text('تأكيد ' + actionTxt); // Modal Title
							modal.find('.modal-body h4').text(modalTitle); // Modal Sub title
							
							// show||hide field reason 
							if(actionRef == '1'){modal.find('.modal-body #reason').hide();}else{modal.find('.modal-body #reason').show();}

							// add value to helper hidden fileds 
							for (var i = 0; i < dataKey.length; i++) {
								modal.find(".modal-body input:hidden[id$='" + dataKey[i] + "']").val(dataValue[i]);
								if (typeof console == 'object') console.log(dataKey[i] + " : " + dataValue[i]);
							}
							
							// type of current button : ok||No
							modal.find(".modal-body input:hidden[id$='actionRef']").val(actionRef);
							
							if($('#LoadModal').length){
								modal.find(".modal-footer .btn-primary").click(function(){
									modal.find(".close").trigger('click')
									openLoadModal(modalTitle);
								});
							}
						});

						// clear modal on close
						$("#confirmModal").on('hide.bs.modal', function (event) {
							var modal	= $(this);
							modal.find('.modal-body textarea.form-control').val('');
							target.removeClass('active');
						});

						return "active";
					  } else {
						return "noactive";
					  }
					});
				});
			});
		}
		// Load 
		function openLoadModal(modalTitle){
			setTimeout(function(){
				$("#LoadModal").modal({
					backdrop: 'static',
					keyboard: false
				});
				$("#LoadModal").on('show.bs.modal', function (event) {
					var modal2	= $(this);
					// type of current button : ok||No
					var projectName = modalTitle;

					modal2.find('.modal-title h4').text('اعتماد المشروع: '+projectName);
					modal2.find('.progress-bar').each(function(){
						$(this).closest('li').removeClass('completed').removeAttr('style');
						$(this).parent().removeAttr('style');
						$(this).removeAttr('style');
					});
				});
				$("#LoadModal").on('hide.bs.modal', function (event) {
					
				});
			}, 500);
		}

		/***********************************************************************************************************
								btnAdd
		 ***********************************************************************************************************/
		if (jQuery('#btnAdd').length > 0) {
			function wellFormClose() {$('.wellForm .form-control').each(function(){if($(this).is('input') || $(this).is('textarea')){$(this).not('.fixField').val('');} else if ($(this).is('select')) {var target = $(this);target.select2().select2('val', '0');}else{}});$('.wellForm .form-control').parent().removeClass('has-error').removeClass('has-success');}
			jQuery('#btnAdd').parent().addClass('toggleWellForm');
			jQuery('#btnAdd a').click(function () {
				var target = $(this).attr('rel').replace('btn', '');
				jQuery(".wellForm:not([id$='"+target+"'])").slideUp();
				jQuery('div[id$="' + target + '"].wellForm').slideToggle(function () { wellFormClose(); });
			});
		}

		/**************************************************************************************************************
							maxLength
		**************************************************************************************************************/
		$('.maxLength').keypress(function(){
			var maxlength = $(this).attr('maxlength');
			var left = maxlength - $(this).val().length;
			if (left < 0) {
				left = 0;
			}
			$(this).parent().find('.help-block').text('باقي ' + left + ' حرف');
		});

		/**************************************************************************************************************
							Form all .form-control
		**************************************************************************************************************/
		if (jQuery('.form-control').length > 0) { // if .form-control Exist
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
		
		if (jQuery('.niceCheck').length > 0) {// niceCheck add styled cheked for each input:checkbox
			jQuery('.niceCheck').each(function(){
				var niceCheck = jQuery(this),
					inputC = jQuery(this).find('input');
				if (inputC.is(':checked')) {niceCheck.addClass('checked');}else{niceCheck.removeClass('checked');}
				jQuery(this).find('label').click(function(){
					if (inputC.is(':checked')) {
						niceCheck.addClass('checked');
						niceCheck.removeClass('has-error');
					}else{
						niceCheck.removeClass('checked');
					}
					
					if($('#selectAll').length) { 
						var lineNbr = $('.results .lines').length;
						var checkedNbr = $('.results .lines input:checked').length;
						if(lineNbr == checkedNbr){
							$('#selectAll input').prop('checked' , true);
							$('#selectAll').addClass('checked');
						}else{
							$('#selectAll input').prop('checked' , false);
							$('#selectAll').removeClass('checked');
						}
					}
				});
			});
		}
		
		if (jQuery('#selectAll').length > 0) { // selectAll button
			$('#selectAll input').click(function(event) {  			 //on click
				if(this.checked) { 									 // check select status
					$('.niceCheck input:checkbox').each(function() { //loop through each checkbox
						$(this).prop('checked' , true);				 //select all checkboxes with class "checkbox1" 
						$(this).parents('.niceCheck').addClass('checked');		 // add class  .checked to parent
					});
				}else{
					$('.niceCheck input:checkbox').each(function() { //loop through each checkbox
						$(this).prop('checked' , false);			 //select all checkboxes with class "checkbox1" 
						$(this).parents('.niceCheck').removeClass('checked');	 // remove class  .checked from parent
					});      
				}
			});
		}

		/**************************************************************************************************************
							.nav-tabs
		**************************************************************************************************************/
		if (jQuery('.nav-tabs').length > 0) { // if mainMenu Exist
			hash = window.location.hash;
			if (hash || hash != '') {
				var url = (hash[0] == '#') ? hash.substring(1) : hash;
				jQuery('.nav-tabs li a').each(function () {
					if (jQuery(this).attr('href') == hash) { 
						jQuery(this).trigger('click')
					}
				});
				//if (typeof console == "object") { console.log(hash); }
				return;
			}
		}

		/**************************************************************************************************************
							.niceField
		**************************************************************************************************************/
			//	niceField
		if ($('.niceField').length > 0) {
			$('.niceField a').click(function (event) {
				$(this).parent().find('input').trigger('click');
			});
			$('.niceField input').change(function (event) {
				var target = $(this).val();
				$(this).parent().find('a').text(target);
			});
		}

		/**************************************************************************************************************
							.rating-tooltip
		**************************************************************************************************************/
		if ($('.rating-tooltip').length > 0) {
			$('.rating-tooltip').rating({
			  extendSymbol: function (rate) {
				$(this).tooltip({
				  container: 'body',
				  placement: 'bottom',
				  title: 'Rate ' + rate
				});
			  }
			});
			/* $('input:hidden.rating-tooltip').each(function(){
				var target = $(this).val();
				if(target > 3) { $(this).parent().addClass('green'); }else if(target < 3) { $(this).parent().addClass('red'); }else{ $(this).parent().addClass('orange'); }
			}); */
		}
	});

	/*===========================================================================================================================================
									Function
	  ===========================================================================================================================================*/
	
	// on resize nav-tabls type2
	function tabsType2Resize() {
		var $listParent	= $('.tabsType2'),
			$widthParent= $listParent.width(), // Compare val 1
			$listItem	= $('.tabsType2 > li'),
			$ItemWidth	= $listItem.width(),
			$nbrItems	= $listItem.length,
			$widthItems	= $ItemWidth * $nbrItems; // Compare val 2
		if($widthParent <= $widthItems){
			$listParent.addClass('nav-justified');
		}else{
			$listParent.removeClass('nav-justified');
		}
	}
}

mainload();
//Sys.WebForms.PageRequestManager.getInstance().add_endRequest(mainload);
// ]]>