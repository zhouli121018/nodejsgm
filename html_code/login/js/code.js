/** 
 * Created by lgy on 2017/10/21. 
 * 图片验证码 
 */
(function ($) { 
 $.fn.imgcode = function (options) { 
  //初始化参数 
  var defaults = { 
   callback:"" //回调函数 
  };
  var key='';
  var src1 = '';
  var src2 = '';
  function getKey(){
   $.ajax({
    url:'/ajax_get_captcha',
    async: false,
    success:function(data){
     key=data.key;
     console.log('key:'+key);
     src1 = "/captcha_img/"+key+".png";
     src2 = "/captcha_img/"+key+".jpg";
    }
   })
  }
  //getKey();
src1 = "img/88.png";
src2 = "img/88.jpg";
  var opts = $.extend(defaults, options);
  return this.each(function () { 
   var $this = $(this);//获取当前对象 
   var html = '<div class="code-k-div">' +
    '<div class="code-con">' +
    '<div class="code-img">' + 
    '<div class="code-img-con">' + 
    '<div class="code-mask"><img src='+src1+'></div>' +
    '<img src='+src2+'></div>' +
    '<i title="刷新" class="icon-login-bg icon-w-25 icon-push"></i>' +
    '</div>' +
    '<div class="code-btn">' + 
    '<div class="code-btn-img code-btn-m"></div>' + 
    '<span>按住滑块，拖动完成上方拼图</span>' + 
    '</div><input type="hidden" id="code-img"  class="img_captcha" value="0" dataDrag="0" name="captcha"/></div></div>';
   $this.html(html);
   //src="../static/img/fresh-active.png"
   //定义拖动参数 
   var $divMove = $(this).find(".code-btn-img"); //拖动按钮 
   var $divWrap = $(this).find(".code-btn");//鼠标可拖拽区域 
   var mX = 0, mY = 0;//定义鼠标X轴Y轴 
   var dX = 0, dY = 0;//定义滑动区域左、上位置 
   var isDown = false;//mousedown标记 
   if(document.attachEvent) {//ie的事件监听，拖拽div时禁止选中内容，firefox与chrome已在css中设置过-moz-user-select: none; -webkit-user-select: none; 
    $divMove[0].attachEvent('onselectstart', function() { 
     return false; 
    }); 
   } 
   //按钮拖动事件 
   $divMove.on({ 
    mousedown: function (e) { 
     //清除提示信息 
     $this.find(".code-tip").html(""); 
     var event = e || window.event; 
     mX = event.pageX; 
     dX = $divWrap.offset().left; 
     dY = $divWrap.offset().top; 
     isDown = true;//鼠标拖拽启 
     $('.code-con').addClass('old');
     $(this).addClass("active"); 
     //修改按钮阴影 
     $divMove.css({"box-shadow":"0 0 8px #666"}); 
    } 
   }); 
   //鼠标点击松手事件 
   $('.code-btn').mouseup(function (e) {
    //if(e.target.nodeName=='I'){
    //  return;
    //}
    if($('.code-con').hasClass('success')){
     return;
    }
    var lastX = $this.find(".code-mask").offset().left - dX - 1; 
    isDown = false;//鼠标拖拽启 
    $divMove.removeClass("active"); 
    //还原按钮阴影 
    $divMove.css({"box-shadow":"0 0 3px #ccc"});
    $('#code-img').val(key);
    console.log(111111111);
    console.log("val:"+$('#code-img').val());
    console.log("x:"+lastX);
    checkcode(lastX);

   }); 
   //滑动事件 
   $divWrap.mousemove(function (event) { 
    var event = event || window.event; 
    var x = event.pageX;//鼠标滑动时的X轴 
    if (isDown) { 
     if(x>(dX+30) && x<dX+$(this).width()-20){ 
      $divMove.css({"left": (x - dX - 20) + "px"});//div动态位置赋值 
      $this.find(".code-mask").css({"left": (x - dX-30) + "px"}); 
     } 
    } 
   });
   //刷新事件
   $('.icon-push').click(function(){
    getKey();
    setTimeout(function(){
     $('.code-mask>img').attr('src',src1);
     $('.code-img-con>img').attr('src',src2);

    },300);
   })
   $('.code-con').mouseenter(function(){
    if(!$('.code-con').hasClass('success')){
     $('.code-img').slideDown();
    }
   })
   $('.code-con').mouseleave(function(){
    //if(!$(this).hasClass('old')){
      $('.code-img').slideUp();
    //}
   })
   //验证数据 
   function checkcode(code){
    var iscur=false; 
    //模拟ajax
    $.ajax({
     url:"/ajax_check_captcha/?id="+key+"&value="+code,
     success:function(data){
      console.log("result:"+data.res);
      if(data.res){
       iscur=true;
       $this.find(".code-img").hide();
       $('.code-con').addClass('success').removeClass('fail');
       $('.code-btn .code-btn-img').hide();
       $('.code-btn>span').html('验证通过');
       $('.code-btn').css({"background":"#2EB837","color":"#fff"});
      }else{
       $('.code-con').addClass('fail').removeClass('success');
       $('.code-btn .code-btn-img').show();
       $this.find(".code-mask").animate({"left":"0px"},200);
       $divMove.animate({"left": "10px"},200);
       $('.code-btn>span').html('验证不通过,请拖动完成上方拼图');
       $('.code-btn').css({"background":"#f54c47","color":"#fff"});
       getKey();
       setTimeout(function(){
        $('.code-mask>img').attr('src',src1);
        $('.code-img-con>img').attr('src',src2);
       },1000)
      }
      console.log($('#code-img').attr('dataDrag'))
     }

    })
    //console.log(Math.abs(code-x));
    //console.log(Math.abs(code-x)<5)

    //setTimeout(function(){
    // if(iscur){
    //  checkcoderesult(1,"验证通过");
    //
    //
    // // opts.callback({code:1000,msg:"验证通过",msgcode:"23dfdf123"});
    // }else{
    //  $divMove.addClass("error");
    //  checkcoderesult(0,"验证不通过");
    //  //opts.callback({code:1001,msg:"验证不通过"});
    //
    //  setTimeout(function() {
    //   $divMove.removeClass("error");
    //   $this.find(".code-mask").animate({"left":"0px"},200);
    //   $divMove.animate({"left": "10px"},200);
    //  },400);
    // }
    //},500)
   }
   //验证结果 
   function checkcoderesult(i,txt){ 
    if(i==0){ 
     $this.find(".code-tip").addClass("code-tip-red"); 
    }else{ 
     $this.find(".code-tip").addClass("code-tip-green"); 
    } 
    $this.find(".code-tip").html(txt); 
   } 
  }) 
 } 
})(jQuery); 