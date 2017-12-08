/**
 * Created by bjwsl-001 on 2017/5/2.
 */

window.onload= function () {
  var imgW=parseFloat($('#banner img').css('width'));
  console.log(imgW);
  $("#banner>div").css('width',2*imgW+'px').css('left',0);
  function carousel(){
    $("#banner>div").animate({left:-imgW+'px'},1000,function(){

      $("#banner>div").children("img:first").insertAfter($("#banner>div").children("img:last"));
      $("#banner>div").css("left", 0);
    })
  }
  var timer=setInterval(carousel,3000);
  //$("#banner>div").mouseenter(function(){
  //  clearInterval(timer);
  //  timer=null;
  //  //$("#banner>div>img").css('display','none');
  //  //$("#banner>div>img.scroll").css('display','block');
  //  //$('#banner>div').css('transform','translatey(-200px) translatez(-200px) rotatex(90deg)');
  //});
  //$("#banner>div").mouseleave(function(){
  //  //$('#banner>div').css('transform','translatey(-200px) translatez(-200px) rotatex(0deg)');
  //  timer=null;
  //  timer=setInterval(carousel,3000);
  //  //$("#banner>div>img").css('display','block');
  //  //$("#banner>div>img.scroll").css('display','none');
  //})

};


