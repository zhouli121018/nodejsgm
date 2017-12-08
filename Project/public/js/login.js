///**
// * Created by bjwsl-001 on 2017/5/16.
// */
//  var form=document.querySelector("#login form");
//var reg=/^[0-9a-zA-Z]{6,12}$/;
//form.uname.onblur=function(){
//  if($(this).val()!=null){
//    if(!reg.test(this.value)){
//      //this.focus();
//      $(this).parent().next().children().html('*用户名格式不正确！*');
//      //alert('用户名格式不正确！');
//      $(this).css('borderColor','red');
//    }else{
//      $(this).css('borderColor','#afa');
//      $(this).parent().next().children().html('OK');
//    }
//  }
//};
//form.upwd.onblur=function(){
//  if($(this).val()!=null){
//    if(!reg.test(this.value)){
//      // this.focus();
//      $(this).parent().next().children().html('*密码格式不正确！*');
//      $(this).css('borderColor','red');
//    }else{
//      $(this).css('borderColor','#afa');
//      $(this).parent().next().children().html('OK');
//    }
//  }
//};
//form.upwdre.onblur=function(){
//  if(this.value!==form.upwd.value){
//    //this.focus();
//    $(this).parent().next().children().html('*两次输入的密码不一致！*');
//    $(this).css('borderColor','red');
//   //alert("两次输入的密码不一致！");
//  }else{
//    $(this).css('borderColor','#afa');
//    $(this).parent().next().children().html('OK');
//  }
//};
//$("#login .close").click(function(){
//  $("#login").hide();
//});
//document.querySelector("#login #regBtn").onclick=function(e){
//  e.preventDefault();
//  if(!reg.test(form.uname.value)){form.uname.focus();return false;}
//  else if(!reg.test(form.upwd.value)){form.upwd.focus();return false;}
//  else if(form.upwdre.value!=form.upwd.value){form.upwdre.focus();return false}
//    $.ajax({
//      url:"/reg_user",
//      data:{uname:form.uname.value,upwd:form.upwd.value},
//      success:function(data){
//          alert(data.msg);
//      }
//    })
//
//};
//
//var loginUid,loginUname;
//$("#login #loginBtn").click(function(e){
//  e.preventDefault();
//  if(!reg.test(form.uname.value)){form.uname.focus();return false;}
//  else if(!reg.test(form.upwd.value)){form.upwd.focus();return false;}
//  else if(form.upwdre.value!=form.upwd.value){form.upwdre.focus();return false}
//  $.ajax({
//    url:"/login_user",
//    data:{uname:form.uname.value,upwd:form.upwd.value},
//    success:function(data){
//      console.log(data);
//      if(data.code>0){
//         loginUid=data.uid;
//         loginUname=data.uname;
//        document.cookie='logUid='+loginUid;
//        document.cookie='logUname='+loginUname;
//        console.log(loginUid,loginUname);
//         $("#login").hide();
//        alert(data.msg);
//      }else{
//        alert(data.msg);
//      }
//    }
//  })
//});
//
