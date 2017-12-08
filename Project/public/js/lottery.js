/**
 * Created by bjwsl-001 on 2017/6/13.
 */

var progress = 0;
//加载图片
var imgPan = new Image();
imgPan.src = 'img/pan.png';
imgPan.onload = function(){
  progress += 75;
  if(progress===100){
    startDraw();
  }
};
var imgPin = new Image();
imgPin.src = 'img/pin.png';
imgPin.onload = function(){
  progress += 25;
  if(progress===100){
    startDraw();
  }
};
//开始绘制静止的圆盘和指针
function startDraw(){
  var cw = imgPan.width;  //圆盘&画布的宽
  var ch = imgPan.height;
  c1.width = cw;
  c1.height = ch;
  var ctx = c1.getContext('2d');
  //先绘制圆盘
  ctx.drawImage(imgPan, 0, 0);
  //再绘制指针
  ctx.drawImage(imgPin, cw/2-imgPin.width/2, ch/2-imgPin.height/2);
  console.dir(ctx);

  $('#luck-lottery #bt').click(function(){
    var deg=0;
    var t=Math.random()*(2000)+2000;
    var prevt=new Date();
    var timer=setInterval(function task(){
      var lt=new Date();
      if(lt-prevt>=t){
        clearInterval(timer);
        timer=null;
        console.log(deg);
        if(deg>0&&deg<=28||deg>88&&deg<=118||deg>148&&deg<=178||deg>208&&deg<=238||deg>268&&deg<=298){
          var msg="幸运奖";
        }else if(deg>58&&deg<=88){
          var msg="一等奖";
        }else if(deg>118&&deg<=148||deg>328&&deg<358){
          var msg="二等奖";
        }else{
          var msg="三等奖";
        }
        alert("恭喜您中了"+msg);
        return;
      }
      deg+=15;deg%=360;
      ctx.clearRect(0,0,cw,ch);
      ctx.drawImage(imgPan,0,0);
      ctx.save();
      ctx.translate(cw/2,ch/2);
      ctx.rotate(deg*Math.PI/180);
      ctx.drawImage(imgPin, -imgPin.width/2, -imgPin.height/2);
      ctx.restore();
    },30)
  });
}

//异步请求当前登录用户的抽奖统计
//$.ajax({
//  url: '/lottery',
//  data: {uid: 5},
//  success: function(data){
//    bt.innerHTML = `开始抽奖(总抽奖次数：${data.total} 剩余次数：${data.total-data.used})`;
//    if(data.total<=data.used){
//      return; //已抽奖次数大于等于总次数，不能再抽奖
//    }
//    bt.disabled = false;
//    bt.onclick = function(){  //点击按钮，开始抽奖
//      //变量：设置一个随机的旋转总时长
//      //变量：记录当前已经旋转的时长
//      //变量：记录当前已经旋转的角度
//      //启动定时器，开始旋转：平移/旋转=>绘圆盘=>恢复=>绘制指针
//    }
//  }
//});
