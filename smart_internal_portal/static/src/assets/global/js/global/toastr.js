!function (document, window, $) {
    "use strict";
    $('.awesome_ok').on('click',function(){
        $.amaran({
            'theme'     :'awesome ok',
            'content'   :{
                title:'Your Download is Ready!',
                message:'1.4 GB',
                info:'my_birthday.mp4',
                icon:'fa fa-download'
            },
            'position'  :'bottom right',
            'outEffect' :'slideBottom',
            'inEffect'  :'slideRight'
        });
    });
    $('.awesome_error').on('click',function(){
        $.amaran({
            'theme'     :'awesome error',
            'content'   :{
                title:'Try again!',
                message:'You are not successfully logged in!',
                info:'',
                icon:'fa fa-times'
            },
            'position'  :'bottom right',
            'outEffect' :'slideBottom',
            'inEffect'  :'slideRight'

        });
    });
    $('.awesome_success').on('click',function(){
        $.amaran({
            'theme'     :'awesome success',
            'content'   :{
                title:'Welcome Back!',
                message:'You are successfully logged in!',
                info:'',
                icon:'fa fa-check-square-o'
            },
            'position'  :'bottom right',
            'outEffect' :'slideBottom',
            'inEffect'  :'slideRight'
        });
    });
    $('.awesome_user').on('click',function(){
        $.amaran({
            'theme'     :'user blue',
            'content'   :{
                img:'../../..//smart_internal_portal/static/src/assets/global/image/img_150x150.png',
                user:'John Walker',
                message:'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Cupiditate, ducimus?'
            },
            'position'  :'bottom right',
            'outEffect' :'slideBottom',
            'inEffect'  :'slideRight'
        });
    });
}(document, window, jQuery);