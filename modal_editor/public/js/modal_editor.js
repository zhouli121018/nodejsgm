/**
 * Created by FQ-041 on 2018/5/11.
 */
$(function () {
    $('.select2').select2();
    $('.colorpicker-component').colorpicker();
//        var arrow_right = `<i class="glyphicon glyphicon-chevron-right pull-right "></i>`;
//        var arrow_down = `<i class="glyphicon glyphicon-chevron-down pull-right "></i>`;
//        $('.panel-title a').
    $('.summernote').summernote({
        height: 200,
        dialogsFade: true,
        tabsize: 2,
        lang: 'zh-CN'
    });


    var tpl = '<div class="actions"><p class="top0"><i class="glyphicon glyphicon-eject"></i></p>' +
        '<p><i class="glyphicon glyphicon-chevron-up"></i></p>' +
        '<p><i class="glyphicon glyphicon-chevron-down"></i></p>' +
        '<p><i class="glyphicon glyphicon-remove"></i></p>' +
        '</div>';
    $('[data-placement="right"]').attr('title',tpl).tooltip();
    $('#popover').attr('data-html',true).attr('data-trigger','focus').attr('data-content',tpl).popover()
    $('#popover').on('hidden.bs.popover', function (e) {
        // do something…
//            console.log(this)

    })

    function showModal(){
        $('#myModal').modal()
    }

    function initPop(){
        var tpl = '<div class="actions">' +
            ' <p class="top0" title="置顶"><i class="glyphicon glyphicon-triangle-top"></i></p>' +
            '<p class="top1" title="上移"><i class="glyphicon glyphicon-chevron-up"></i></p>' +
            ' <p class="down1" title="下移"><i class="glyphicon glyphicon-chevron-down"></i></p>' +
            '<p class="down0" title="置底"><i class="glyphicon glyphicon-triangle-bottom"></i></p>' +
            '<p class="remove1" title="删除"><i class="glyphicon glyphicon-remove"></i></p>' +
            '</div>'

        $('.set_popover_btn').attr('data-html',true).attr('data-content',tpl).popover();

    }

    var bodyS = function(iframe) {
        var i;
        var obj;
        //设置 "body"
        obj = iframe.contentWindow.document.body;
        obj.style.overflowX  = 'auto';
        obj.style.overflowY  = 'hidden';
        obj.style.wordWrap   = 'break-word';
        obj.style.fontSize = '12px';
        var head = iframe.contentWindow.document.getElementsByTagName('head')[0];
        obj = iframe.contentWindow.document.getElementsByTagName('a');
        for(i=0; i<obj.length; i++) {
            obj[i].target = "_blank";
        }
        obj = iframe.contentWindow.document.getElementsByTagName('p');
        for(i=0; i<obj.length; i++) {
//      obj[i].style.marginTop = "5px";
//      obj[i].style.marginBottom = "5px";
        }
    };

    var set_btn='<a class="btn btn-sm btn-warning set_popover_btn" role="button" tabindex="0" data-trigger="focus" style="position:absolute;right:-50px;"><i class="glyphicon glyphicon-cog"></i></a>';

    function init(){
        var button = ' <div class="row">' + set_btn+
            '<div class="col-sm-12 no-padding button_box">' +
            '<div class="text-center" style="min-height:50px;"><input type="button" value="我的按钮" class="btn btn-default">' +
            '</div>' +
            '</div></div>'
        var text = '<div class="row text_row" style="min-height:50px;">'+set_btn+
            '<div class="col-sm-12 no-padding text_box" >content' +
            '    </div></div>';
        var img = '<div class="row img_row">'+set_btn+'<div class="col-sm-12 no-padding image_box">' +
            '     <div class="text-center" style="border:1px solid #cdcdcd;background:#F5F5F5;min-height:50px;vertical-align: middle"><img src="img/masterImage.png" style="width:20px;" alt="img"></div>' +
            '    </div></div>';
        var spacer = '<div class="row">'+set_btn+'<div class="col-sm-12 no-padding spacer_box">' +
            '    <p style="min-height:50px;"></p>' +
            '    </div></div>';
        var ruler = '<div class="row">'+set_btn+'<div class="col-sm-12 no-padding ruler_box">' +
            '    <div style="min-height:50px;border-top:2px solid #666;"></div>' +
            '    </div></div>';

        var button_noset = '<div class="row">' +
            '<div class="col-sm-12 no-padding button_box">' +
            '<div class="text-center" style="min-height:50px;"><input type="button" value="我的按钮" class="btn btn-default">' +
            '</div>' +
            '</div></div>';
        var text_noset = '<div class="row text_row" style="min-height:50px;"><div class="col-sm-12 no-padding text_box">content' +
            '</div></div>';
        var img_noset = '<div class="row img_row"><div class="col-sm-12 no-padding image_box">' +
            '<div class="text-center" style="border:1px solid #cdcdcd;background:#F5F5F5;min-height:50px;vertical-align: middle"><img src="img/masterImage.png" style="width:20px;" alt="img"></div>' +
            '</div></div>';
        var spacer_noset = '<div class="row">' +
            '<div class="col-sm-12 no-padding spacer_box">' +
            '<p style="min-height:50px;"></p>' +
            '</div></div>';
        var ruler_noset = '<div class="row">' +
            '<div class="col-sm-12 no-padding ruler_box">' +
            '<div style="min-height:50px;border-top:2px solid #666;"></div>' +
            '</div></div>';


//            var ibody = document.getElementById('mail-iframe').contentWindow.document.body;



        $('.add_btn').click(function(){
            $('.editor-box').append(button);
            initPop();
        })
        $('.add_img').click(function(){
            $('.editor-box').append(img)
            initPop();
        })
        $('.add_text').click(function(){
            $('.editor-box').append(text)
            initPop();
        })
        $('.add_space').click(function(){
            $('.editor-box').append(spacer)
            initPop();
        })
        $('.add_ruler').click(function(){
            $('.editor-box').append(ruler)
            initPop();
        })

        $('#myModal .item-box').click(function(){
            $('#myModal').modal('hide');
            var type = $(this).find('img').attr('title');
            $('.editor-box .cur_box').parents('.editor-col').removeClass('editor-col');
            if(type == 'text'){
                $('.editor-box .cur_box').parent().html(text_noset);
            }else if(type == 'image'){
                $('.editor-box .cur_box').parent().html(img_noset);
            }else if(type == 'button'){
                $('.editor-box .cur_box').parent().html(button_noset);
            }else if(type == 'spacer'){
                $('.editor-box .cur_box').parent().html(spacer_noset);
            }else if(type == 'ruler'){
                $('.editor-box .cur_box').parent().html(ruler_noset);
            }
            initPop();
        })


    }
    init();

    $('.add-layout').click(function(){
        $('.select-layout-box').toggle();
    })


    var row = '<div class="row"> '+set_btn+'' +
        '<div class="col-sm-12 editor-col">' +
        '<div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div>' +
        '</div></div>'
    var row2 = '<div class="row"> '+set_btn +
        '<div class="col-sm-6 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> <div class="col-sm-6 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> </div>'
    var row3 = '<div class="row">'+set_btn+'<div class="col-sm-4 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> ' +
        '<div class="col-sm-4 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> ' +
        '<div class="col-sm-4 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> </div>'
    var row4 = '<div class="row">'+set_btn+'<div class="col-sm-3 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> ' +
        '<div class="col-sm-3 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> ' +
        '<div class="col-sm-3 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> ' +
        '<div class="col-sm-3 editor-col"><div class="text-center box-init"><i class="glyphicon glyphicon-plus"></i></div></div> </div>'
    $('.layout-img-box p').click(function(){
        $('.select-layout-box').hide();
        var index = $(this).attr('data-lay');
        if(index == '1'){
            $('.editor-box').append(row);
            initPop();
        }else if(index == '2'){
            $('.editor-box').append(row2);
            initPop();
        }else if(index == '3'){
            $('.editor-box').append(row3);
            initPop();
        }else if(index == '4'){
            $('.editor-box').append(row4);
            initPop();
        }

    })
    $('body').on('click','.editor-col .box-init',function(){
        //$('#myModal', window.parent.document).modal();
        $(this).addClass('cur_box');
        showModal();
    })
    $('.editor-box').on('click','.actions .remove1',function(){
        $(this).parents('.popover').parent().remove();
    })
    $('.editor-box').on('click','.actions .top0',function(){
        var $first = $('.editor-box>.row:eq(0)');
        $(this).parents('.popover').parent().insertBefore($first);
    })
    $('.editor-box').on('click','.actions .top1',function(){
        var $prev = $(this).parents('.popover').parent().prev();
        $(this).parents('.popover').parent().insertBefore($prev);
    })
    $('.editor-box').on('click','.actions .down1',function(){
        var $next = $(this).parents('.popover').parent().next();
        $(this).parents('.popover').parent().insertAfter($next);
    })
    $('.editor-box').on('click','.actions .down0',function(){
        var $last = $('.editor-box>.row:last-child');
        $(this).parents('.popover').parent().insertAfter($last);
    })
//        $('.editor-box').on('click','.remove1',function(){
//            $(this).parents('.popover').parent().remove();
//        })
//        $('.editor-box').on('click','.remove1',function(){
//            $(this).parents('.popover').parent().remove();
//        })







})

function initImage(ele){
    $(ele).fileinput({
        'allowedFileExtensions' : ['jpg', 'png','gif'],
        uploadExtraData: {kvId: '10'}
    });
}

function initImg(ele){
    $(ele).fileinput({
        showUpload: false,
        showCaption: false,
        browseClass: "btn btn-primary",
        fileType: "any",
        previewFileIcon: "<i class='glyphicon glyphicon-king'></i>"
    });
}
//initImage("#file-4");
initImg("#file-3")
initImg("#editor_img_file")


$('#global_color>input').change(function(){
    $('.content').css('background-color',$(this).val())
})
$('.global_padding').change(function(){
    $('.content').css('paddingTop',$(this).val()+'px')
    $('.content').css('paddingBottom',$(this).val()+'px')
})
$('.global_padding_lr').change(function(){
    $('.content').css('paddingLeft',$(this).val()+'px')
    $('.content').css('paddingRight',$(this).val()+'px')
    console.log($(this).val())
//        console.log($('.main-editor').html())
})
$('.global_width').change(function(){
    $('.content').css('width',$(this).val()+'px')
//        console.log($('.main-editor').html())
})
$('.global_bg').change(function(){
    var bb=encodeURIComponent($(this).val());
    var nnow=decodeURIComponent(bb);
    $('.content').css('backgroundImage',"url("+nnow+")");
    console.log($(this).val())
})
$('#img_modal').on('click','p.select_bg',function(){
    $('#img_modal p.select_bg').removeClass('active');
    $(this).addClass('active');
})
$('#img_modal .sure_bg_btn').click(function(){
    $('#img_modal').modal('hide');
    var src = $("#img_modal p.select_bg.active img").attr('src')
    $('.content').css('backgroundImage',"url("+src+")");
})
$('.cancel_global_bg').click(function(){
    $('.content').css('backgroundImage',"none");
})


$('.body').click(function(){
    $('.global_set').addClass('active').siblings().removeClass('active');
})
$('body').on('click','.text_row',function(){
    $('.editor_font').addClass('active').siblings().removeClass('active');
    $('body .current_text_row').removeClass('current_text_row');
    $(this).addClass('current_text_row');
    var $cur_div = $(this).find('>div');
    var content = $(this).find('>div').html();
    var pt = parseFloat($cur_div.css('paddingTop') )|| 0;
    var pl = parseFloat($cur_div.css('paddingLeft')) || 0;
    var pr = parseFloat($cur_div.css('paddingRight')) || 0;
    var pb = parseFloat($cur_div.css('paddingBottom')) || 0;
    $('.note-editable.panel-body').html(content);
    $('.editor_font .text_pt').val(pt);
    $('.editor_font .text_pl').val(pl);
    $('.editor_font .text_pr').val(pr);
    $('.editor_font .text_pb').val(pb);
})
function auto_text(){
    var con =  $('.summernote').summernote('code');
    $('.text_row.current_text_row>div').html(con)
}
$('.summernote').on('summernote.keyup', function(we, e) {
//        console.log('Key is released:', e.keyCode);
    console.log(we);
    auto_text();
});
$('#summernote').on('summernote.paste', function(e) {
    auto_text();
});
$('#summernote').on('summernote.change', function(we, contents, $editable) {
    console.log('summernote\'s content is changed.');
    auto_text();
});
$('#summernote').on('summernote.blur', function() {
    console.log('Editable area is focused');
    auto_text();
});
$('.editor_font .text_pt').change(function(){
    var pt = $(this).val();
    $('.text_row.current_text_row>div').css('paddingTop',pt+'px');
})
$('.editor_font .text_pr').change(function(){
    var pt = $(this).val();
    $('.text_row.current_text_row>div').css('paddingRight',pt+'px');
})
$('.editor_font .text_pb').change(function(){
    var pt = $(this).val();
    $('.text_row.current_text_row>div').css('paddingBottom',pt+'px');
})
$('.editor_font .text_pl').change(function(){
    var pt = $(this).val();
    $('.text_row.current_text_row>div').css('paddingLeft',pt+'px');
})
$('.editor_font .text_bgcolor').change(function(){
    var pt = $(this).val();
    $('.text_row.current_text_row>div').css('backgroundColor',pt);
})

$('body').on('click','.img_row',function(){
    $('.editor_image').addClass('active').siblings().removeClass('active');
    $('body .current_img_row').removeClass('current_img_row');
    $(this).addClass('current_img_row');
})