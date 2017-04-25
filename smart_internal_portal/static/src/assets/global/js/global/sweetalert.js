!function (document, window, $) {
    "use strict";

    $('[data-plugin="sweetalert"]').on('click',function () {
        var $this = $(this),
            $options = $.extend({}, $this.data());
        swal($options).catch(swal.noop)
    });

    $('.warning.confirm').on('click', function () {
        swal({
            title: 'Are you sure?',
            text: 'You won\'t be able to revert this!',
            type: 'warning',
            showCancelButton: true,
            confirmButtonClass: "btn btn-primary flat-buttons waves-effect waves-button",
            cancelButtonClass: "btn btn-danger flat-buttons waves-effect waves-button",
            buttonsStyling: false,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then(function () {
            swal({
                title: 'Deleted!',
                type: 'success',
                text: 'Your file has been deleted!',
                confirmButtonClass: "btn btn-primary flat-buttons waves-effect waves-button",
                cancelButtonClass: "btn btn-danger flat-buttons waves-effect waves-button",
                buttonsStyling: false
            })
        }).catch(swal.noop)
    })

    $('.warning.cancel').on('click', function () {
        swal({
            title: 'Are you sure?',
            text: 'Buttons below are styled with bootstrap classes',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'No, cancel!',
            confirmButtonClass: 'btn btn-primary flat-buttons waves-effect waves-button',
            cancelButtonClass: 'btn btn-danger flat-buttons waves-effect waves-button',
            buttonsStyling: false
        }).then(function () {
            swal({
                title: 'Deleted!',
                type: 'success',
                text: 'Your file has been deleted!',
                confirmButtonClass: "btn btn-primary flat-buttons waves-effect waves-button",
                cancelButtonClass: "btn btn-danger flat-buttons waves-effect waves-button",
                buttonsStyling: false
            })
        }, function (dismiss) {
            // dismiss can be 'cancel', 'overlay', 'close', 'timer'
            if (dismiss === 'cancel') {
                swal({
                    title: 'Cancelled',
                    type: 'error',
                    text: 'Your imaginary file is safe :)',
                    confirmButtonClass: "btn btn-primary flat-buttons waves-effect waves-button",
                    cancelButtonClass: "btn btn-danger flat-buttons waves-effect waves-button",
                    buttonsStyling: false
                })
            }
        })
    })

    $('.ajax-request').on('click', function () {
        swal({
            title: 'Submit email to run ajax request',
            input: 'email',
            showCancelButton: true,
            confirmButtonText: 'Submit',
            width: 600,
            confirmButtonClass: 'btn btn-primary flat-buttons waves-effect waves-button',
            cancelButtonClass: 'btn btn-danger flat-buttons waves-effect waves-button',
            buttonsStyling: false,
            showLoaderOnConfirm: true,
            preConfirm: function (email) {
                return new Promise(function (resolve, reject) {
                    setTimeout(function () {
                        if (email === 'taken@example.com') {
                            reject('This email is already taken.')
                        } else {
                            resolve()
                        }
                    }, 2000)
                })
            },
            allowOutsideClick: false
        }).then(function (email) {
            swal({
                type: 'success',
                title: 'Ajax request finished!',
                html: 'Submitted email: ' + '<strong>' + email + '</strong>',
                confirmButtonClass: 'btn btn-primary flat-buttons waves-effect waves-button',
                cancelButtonClass: 'btn btn-danger flat-buttons waves-effect waves-button',
                buttonsStyling: false
            })
        }).catch(swal.noop)
    })
    $('.chaining-modals').on('click', function () {
        swal.setDefaults({
            input: 'text',
            confirmButtonText: 'Next &rarr;',
            showCancelButton: true,
            animation: false,
            confirmButtonClass: 'btn btn-primary flat-buttons waves-effect waves-button',
            cancelButtonClass: 'btn btn-danger flat-buttons waves-effect waves-button',
            buttonsStyling: false,
            progressSteps: ['1', '2', '3']
        })

        var steps = [
            {title: 'Question 1', text: 'Chaining swal2 modals is easy'},
            'Question 2',
            'Question 3'
        ]

        swal.queue(steps).then(function (result) {
            swal.resetDefaults()
            swal({
                title: 'All done!',
                html: 'Your answers: <pre>' + JSON.stringify(result) + '</pre>',
                confirmButtonText: 'Lovely!',
                showCancelButton: false,
                confirmButtonClass: 'btn btn-primary flat-buttons waves-effect waves-button',
                buttonsStyling: false
            }).catch(swal.noop)
        }, function () {
            swal.resetDefaults()
        })
    })
}(document, window, jQuery);