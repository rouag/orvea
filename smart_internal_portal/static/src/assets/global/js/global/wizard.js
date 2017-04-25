!function (document, window, $) {
    "use strict";
    // $(function () {
        $('#wizard-validation').smartWizard({
            transitionEffect: 'slideleft',
            onLeaveStep: leaveAStepCallback,
            reverseButtonsOrder: false,
            keyNavigation: false,
            onFinish: onFinishCallback
        });

        function leaveAStepCallback(obj) {
            var step_num = obj.attr('rel');
            return validateSteps(step_num);
        }

        function onFinishCallback() {
            if (validateAllSteps()) {
                $('form').submit();
            }
        }

        function validateAllSteps() {
            var isStepValid = true;

            if (validateStep1() == false) {
                isStepValid = false;
                $('#wizard-validation').smartWizard('setError', {stepnum: 1, iserror: true});
            } else {
                $('#wizard-validation').smartWizard('setError', {stepnum: 1, iserror: false});
            }

            if (validateStep3() == false) {
                isStepValid = false;
                $('#wizard-validation').smartWizard('setError', {stepnum: 3, iserror: true});
            } else {
                $('#wizard-validation').smartWizard('setError', {stepnum: 3, iserror: false});
            }

            if (!isStepValid) {
                $('#wizard-validation').smartWizard('showMessage', 'Please correct the errors in the steps and continue');
            }

            return isStepValid;
        }


        function validateSteps(step) {
            var isStepValid = true;
            // validate step 1
            if (step == 1) {
                if (validateStep1() == false) {
                    isStepValid = false;
                    $('#wizard-validation').smartWizard('showMessage', 'Please correct the errors in step' + step + ' and click next.');
                    $('#wizard-validation').smartWizard('setError', {stepnum: step, iserror: true});
                } else {
                    $('#wizard-validation').smartWizard('setError', {stepnum: step, iserror: false});
                }
            }

            // validate step3
            if (step == 3) {
                if (validateStep3() == false) {
                    isStepValid = false;
                    $('#wizard-validation').smartWizard('showMessage', 'Please correct the errors in step' + step + ' and click next.');
                    $('#wizard-validation').smartWizard('setError', {stepnum: step, iserror: true});
                } else {
                    $('#wizard-validation').smartWizard('setError', {stepnum: step, iserror: false});
                }
            }

            return isStepValid;
        }

        function validateStep1() {
            var isValid = true;
            // Validate Username
            var un = $('#username').val();
            if (!un && un.length <= 0) {
                isValid = false;
                $('#msg_username').html('Please fill username').show();
            } else {
                $('#msg_username').html('').hide();
            }

            // validate password
            var pw = $('#password').val();
            if (!pw && pw.length <= 0) {
                isValid = false;
                $('#msg_password').html('Please fill password').show();
            } else {
                $('#msg_password').html('').hide();
            }

            // validate confirm password
            var cpw = $('#cpassword').val();
            if (!cpw && cpw.length <= 0) {
                isValid = false;
                $('#msg_cpassword').html('Please fill confirm password').show();
            } else {
                $('#msg_cpassword').html('').hide();
            }

            // validate password match
            if (pw && pw.length > 0 && cpw && cpw.length > 0) {
                if (pw != cpw) {
                    isValid = false;
                    $('#msg_cpassword').html('Password mismatch').show();
                } else {
                    $('#msg_cpassword').html('').hide();
                }
            }
            return isValid;
        }

        function validateStep3() {
            var isValid = true;
            //validate email  email
            var email = $('#email').val();
            if (email && email.length > 0) {
                if (!isValidEmailAddress(email)) {
                    isValid = false;
                    $('#msg_email').html('Email is invalid').show();
                } else {
                    $('#msg_email').html('').hide();
                }
            } else {
                isValid = false;
                $('#msg_email').html('Please enter email').show();
            }
            return isValid;
        }

        // Email Validation
        function isValidEmailAddress(emailAddress) {
            var pattern = new RegExp(/^(("[\w-\s]+")|([\w-]+(?:\.[\w-]+)*)|("[\w-\s]+")([\w-]+(?:\.[\w-]+)*))(@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$)|(@\[?((25[0-5]\.|2[0-4][0-9]\.|1[0-9]{2}\.|[0-9]{1,2}\.))((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){2}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\]?$)/i);
            return pattern.test(emailAddress);
        }
    // });

}(document, window, jQuery);
