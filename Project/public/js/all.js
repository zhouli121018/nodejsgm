/**
 * Created by bjwsl-001 on 2017/5/4.
 */
$(function(){
  if(sessionStorage['loginUid']!=null){
    $("#fixed-right li.user a").css('background','#ff6637');
    var data=sessionStorage['loginUid'];
    $.ajax({
      type:'GET',
      url:'/shoppingCart/count',
      data:{uid:data},
      success:function(count){
        //console.log(count.c);
        count.c=count.c||0;
        console.log(count);
          $("#fixed-right li.sc .badge").html(count.c)
      }
    })
  }


  $("body").on("click","a:has(img)",function(e){
    e.preventDefault();
  });

  $("#index button:contains('购买')").click(function(){
    //if(sessionStorage['loginUid']==undefined){
    //  $("#login").show();
    //}else{
    //  var uid=sessionStorage['uid'];
    //  sessionStorage['pname']=$(this).prev().prev().text();
    //  sessionStorage['price']=parseFloat($(this).prev().html().slice(1));
    //  sessionStorage['scount']=1;
    //  sessionStorage['pic']=$(this).parent().prev().attr('src');
    //  location.href='order.html';
    //}
    if(sessionStorage['loginUid']==undefined){
      $("#login").show();
    }else{
      var arr=[];
      arr.push({
        pid:$(this).parent().prev().attr('alt'),
        pic:$(this).parent().prev().attr('src'),
        count:1,
        price:$(this).prev().find('b').html().slice(1),
        pname:$(this).prev().prev().find('a').html()
      });
      var str=JSON.stringify(arr);
      sessionStorage['orderDetails']=str;
      location.href='order.html';
    }
  })

});
$("#header").load("header.html",function(){
  if(sessionStorage['loginUname']!=null){
    var html=`Hi!欢迎回来--<a href="usercenter.html">[${sessionStorage['loginUname']}]</a>&nbsp;&nbsp;<a id="logout" href="${sessionStorage['loginUid']}">[退出登录]</a>`;
    $("#header #fixed-top>div").html(html);
    $("#fixed-top>div").css('background','rgba(255,50,50,.3)');
    $("#header #logout").click(function(e){
      e.preventDefault();
      if(window.confirm('确认退出吗？')){
        var html=`欢迎来到我的商城--&nbsp;
           <a href="#" class="login">[登录]</a>
           <a href="#" class="register">[注册]</a>`;
        $("#header #fixed-top>div").html(html);
        sessionStorage.clear();
        $("#fixed-right li.sc .badge").html(0);
        location.href='index.html';
      }
    })
  }
});
$("#footer").load('footer.html');
$("#logAreg").load('login.html',function(){
  var form=document.querySelector("#register form");
  var reg=/^[0-9a-zA-Z]{6,12}$/;
  form.uname.onblur=function(){
    if($(this).val()!=null){
      if(!reg.test(this.value)){
        //this.focus();
        $(this).parent().next().children().html('*请输入6-12位数字或字母*');
        //alert('用户名格式不正确！');
        $(this).css('borderColor','red');
      }else{
        $(this).css('borderColor','#afa');
        $(this).parent().next().children().html('OK');
      }
    }
  };
  form.upwd.onblur=function(){
    if($(this).val()!=null){
      if(!reg.test(this.value)){
        // this.focus();
        $(this).parent().next().children().html('*请输入6-12位数字或字母！*');
        $(this).css('borderColor','red');
      }else{
        $(this).css('borderColor','#afa');
        $(this).parent().next().children().html('OK');
      }
    }
  };
  form.upwdre.onblur=function(){
    if(this.value!==form.upwd.value){
      //this.focus();
      $(this).parent().next().children().html('*两次输入的密码不一致！*');
      $(this).css('borderColor','red');
      //alert("两次输入的密码不一致！");
    }else{
      $(this).css('borderColor','#afa');
      $(this).parent().next().children().html('OK');
    }
  };
  $("#register .close").click(function(){
    $("#register").hide();
  });
  $("#login .close").click(function(){
    $("#login").hide();
  });
  document.querySelector("#register #regBtn").onclick=function(e){
    e.preventDefault();
    if(!reg.test(form.uname.value)){form.uname.focus();return false;}
    else if(!reg.test(form.upwd.value)){form.upwd.focus();return false;}
    else if(form.upwdre.value!=form.upwd.value){form.upwdre.focus();return false}
    $.ajax({
      url:"/reg_user",
      data:{uname:form.uname.value,upwd:form.upwd.value},
      success:function(data){
        alert(data.msg);
        $("#register").hide();
        $("#login").show();
      }
    })

  };


  $("#login #lregBtn").click(function(e){
    e.preventDefault();
    $("#login").hide();
    $("#register").show();
  });

  $("#register #rloginBtn").click(function(e){
    e.preventDefault();
    $("#register").hide();
    $("#login").show();
  });

  $("#login #loginBtn").click(function(e){
    e.preventDefault();
    var data=$("#login form.form-horizontal").serialize();
    //console.log(data);
    $.ajax({
      url:"/login_user",
      data:data,
      success:function(data){
        console.log(data);
        if(data.code>0){
          sessionStorage['loginUid']=data.uid;
          sessionStorage['loginUname']=data.uname;
          //document.location.reload();
          $("#login").hide();
          var html=`Hi!欢迎回来--${sessionStorage['loginUname']}&nbsp;&nbsp;<a id="logout" href="${sessionStorage['loginUid']}">[退出登录]</a>`;
          $("#header #fixed-top>div").html(html);
          $("#fixed-top>div").css('background','rgba(255,50,50,.3)');
          $("#header #logout").click(function(e){
            e.preventDefault();
            if(window.confirm('确认退出吗？')){
              var html=`欢迎来到我的商城--&nbsp;
           <a href="#" class="login">[登录]</a>
           <a href="#" class="register">[注册]</a>`;
              $("#header #fixed-top>div").html(html);
              sessionStorage.clear();
              $("#fixed-right li.sc .badge").html(0);
              location.href='index.html';
            }
          });
          $("#fixed-right li.user a").css('background','#ff6637');
          var data=sessionStorage['loginUid'];
          $.ajax({
            type:'GET',
            url:'/shoppingCart/count',
            data:{uid:data},
            success:function(count){
              console.log(count.c);
              if(count.c==null){
                count.c=0;
              }
              $("#fixed-right li.sc .badge").html(count.c)
            }
          })
        }else{
          alert(data.msg);
        }
      }
    })
  });
});
$("#rightFixed").load("rightFixed.html",function(){
  if(sessionStorage['loginUid']!=null){
    $("#fixed-right li.user a").css('background','#ff6637');
    var data=sessionStorage['loginUid'];
    $.ajax({
      type:'GET',
      url:'/shoppingCart/count',
      data:{uid:data},
      success:function(count){
        //console.log(count.c);
        $("#fixed-right li.sc .badge").html(count.c)
      }
    })
  }

});
//var imgs=document.querySelectorAll(".main-top img");
//for(var i=0;i<imgs.length;i++){
//  imgs[i].onmouseenter=function () {
//    $(this).addClass('scale');
//  };
//  imgs[i].onmouseleave=function () {
//    $(this).removeClass('scale');
//  };
//}
$('body').on('mouseenter','img',function(){
  if($(this).parents('#banner').length==0&&$(this).parents('.col-sm-12').length==0){
    $(this).addClass('scale');
    //$(this).parent().css('overflow','hidden');
  }
});
$('body').on('mouseleave','img',function(){
  $(this).removeClass('scale');
});
$("#header").on("click","nav>ul>li",function(){
  $(this).addClass("active").siblings().removeClass('active');
  $(this).mouseleave=null;
});
$("#header").on("mouseenter","nav>ul>li",function(){
  $(this).addClass("active");
});
$("#header").on("mouseleave","nav>ul>li",function(){
  $(this).removeClass("active");
});

$("#header").on('click','#fixed-top>div a.login',function(e){
  e.preventDefault();
  $("#login").show();
});
$("#header").on('click','#fixed-top>div a.register',function(e){
  e.preventDefault();
  $("#register").show();
});

///////////product-details///////////////////////////////////


$('#header').on('keyup','#head #search',function(){
  var str=$(this).val();
  if(str.length==0){
    return;
  }
  $.ajax({
    type:'GET',
    url:'/search/product',
    data:{kw:$(this).val()},
    success:function(data){
      //console.log(data);
      if(data.length!==0){
        for(var i=0,html='';i<data.length;i++){
          html+=`<a href="${data[i].pid}">${data[i].pname}</a> `;
          if(i==4){
            break;
          }
        }
        $("#tips").html(html);
        var html2=`<div class="row result">`;
        for(var j=0;j<data.length;j++){
          var o=data[j];
          html2+=`<div class="col-sm-6 col-md-3">
            <div class="thumbnail">
              <img src="${o.pic}" alt="${o.pid}" class="img-responsive">
              <div class="caption">
                <h3>${o.pname}</h3>
                <p>市场价：<i>￥${o.lastprice.toFixed(2)}</i></p>
                <p>价格：<b>￥${o.price.toFixed(2)}</b></p>
                <p><a href="${o.pid}" class="btn btn-default">购 买</a></p>
              </div>
            </div>
          </div>`;
        }
        html2+=`</div>`;
        $('.search-details').html(html2);
      }
    }
  })
});

$('.search-details').on('click','.caption>p>a',function(e){
  e.preventDefault();
  //if(sessionStorage['loginUid']==undefined){
  //  $("#login").show();
  //}else{
  //  var uid=sessionStorage['uid'];
  //  sessionStorage['pic']=$(this).parent().parent().prev().attr('src');
  //  var pid=$(this).attr('href');
  //  sessionStorage['pid']=pid;
  //  sessionStorage['pname']=$(this).parent().parent().children('h3').html();
  //  sessionStorage['price']=$(this).parent().prev().html().slice(4);
  //  sessionStorage['scount']=1;
  //  location.href='order.html';
  //}
  if(sessionStorage['loginUid']==undefined){
    $("#login").show();
  }else{
    var arr=[];
    arr.push({
      pid:$(this).parents('.caption').prev().attr('alt'),
      pic:$(this).parents('.caption').prev().attr('src'),
      count:1,
      price:$(this).parent().prev().find('b').html().slice(1),
      pname:$(this).parents('.caption').find('h3').html()
    });
    var str=JSON.stringify(arr);
    sessionStorage['orderDetails']=str;
    location.href='order.html';
  }
});
$('#importedSnacks').on('click','dl button',function(){
  //if(sessionStorage['loginUid']==undefined){
  //  $("#login").show();
  //}else{
  //  var uid=sessionStorage['uid'];
  //  sessionStorage['pic']=$(this).parent().parent().find('img').attr('src');
  //  var pid=$(this).parent().parent().find('img').attr('alt');
  //  sessionStorage['pid']=pid;
  //  sessionStorage['pname']=$(this).parent().prev().prev().text();
  //  sessionStorage['price']=parseFloat($(this).parent().prev().children('h3').html().slice(1)).toFixed(2);
  //  sessionStorage['scount']=1;
  //  location.href='order.html';
  //}
  if(sessionStorage['loginUid']==undefined){
    $("#login").show();
  }else{
    var arr=[];
    arr.push({
      pid:$(this).parents('dl').find('img').attr('alt'),
      pic:$(this).parents('dl').find('img').attr('src'),
      count:1,
      price:$(this).parents('dl').find('h3 span').html().slice(1),
      pname:$(this).parents('dl').find('p>a').html()
    });
    var str=JSON.stringify(arr);
    sessionStorage['orderDetails']=str;
    location.href='order.html';
  }
});

$('body').on('click','img',function(){
  $.ajax({
    url:'/detail',
    data:{src:$(this).attr('src')},
    success:function(data){
      console.log(data.length==0);
      console.log(data);
      if(data.length!=0){
        console.log(JSON.stringify(data));
        sessionStorage['list']=JSON.stringify(data);
       // document.cookie=JSON.stringify(data);
        window.location.href='detail.html';
      }
    }
  })
});

$("a[href='#']").click(function(e){
  e.preventDefault();

});

//购物车详情
$('#rightFixed').on('click','li.sc a',function(e){
  e.preventDefault();
  if(sessionStorage['loginUid']==null){
    $("#login").show();
  }else{
    location.href='shoppingCart.html';
  }
});

$('#header').on('click','h1',function(){
  location.pathname='index.html'
})



