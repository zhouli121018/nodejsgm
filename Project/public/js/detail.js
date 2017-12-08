$(function(){

    //console.log(document.cookie);
    var d=JSON.parse(sessionStorage['list']);
   console.log(typeof d,d);
        var html=`
  <div class="left">
    <p>
      <img src="${d.pic}" class="img-responsive" alt="${d.pid}"/>
    </p>
    <p>
      <a href="#"><span class="glyphicon glyphicon-star-empty"></span> 收藏</a>
      <a href="#"><span class="glyphicon glyphicon-star-empty"></span> 分享</a>
    </p>
    <ul class="pager">
      <li class="previous">
        <a href="${d.pid-1}">上一个</a>
      </li>
      <li class="next">
        <a href="${parseInt(d.pid)+1}">下一个</a>
      </li>
    </ul>
  </div>
  <div class="right">
    <h3>${d.pname}</h3>
    <div class="price">价格：<b>&yen;${d.price.toFixed(2)}</b> <i>&yen;${d.lastprice.toFixed(2)}</i></div>
    <p>评论：0条 <span>收藏：0</span></p>
    <div class="count-buy">
      <!--<p>购买数量：</p>-->
      <!--<div>-->
        <!--<p>1</p>-->
        <!--<a><span class="glyphicon glyphicon-triangle-top"></span></a>-->
        <!--<a><span class="glyphicon glyphicon-triangle-bottom"></span></a>-->
      <!--</div>-->
      <span>购买数量：</span>
        <button type="button">-</button>
        <input type="number" required min="1" name="scount" value="1"/>
        <button type="button">+</button>
    </div>
    <button type="button" class="btn1" title="${d.pid}">
      <span class="glyphicon glyphicon-shopping-cart"></span>
      加入购物车
    </button>
    <button type="button" class="btn2" title="${d.pid}">
      立即购买
    </button>`;
  $('div#details').html(html);
  $('div#details').on('click','div.left>ul.pager>li>a',function(e){
      e.preventDefault();
      //console.log($(this).attr('href'));
      if($(this).attr('href')==0){
        $(this).attr('href',27);
      }else if($(this).attr('href')==28){
        $(this).attr('href',1);
      }
      $.ajax({
          url:'/detail_pn',
          data:{pid:$(this).attr('href')},
          success:function(d){
              //console.log(d);
              var html=`
  <div class="left">
    <p>
      <img src="${d.pic}" class="img-responsive" alt="${d.pid}"/>
    </p>
    <p>
      <a href="#"><span class="glyphicon glyphicon-star-empty"></span> 收藏</a>
      <a href="#"><span class="glyphicon glyphicon-star-empty"></span> 分享</a>
    </p>
    <ul class="pager">
      <li class="previous">
        <a href="${d.pid-1}">上一个</a>
      </li>
      <li class="next">
        <a href="${parseInt(d.pid)+1}">下一个</a>
      </li>
    </ul>
  </div>
  <div class="right">
    <h3>${d.pname}</h3>
    <div class="price">价格：<b>&yen;${d.price.toFixed(2)}</b> <i>&yen;${d.lastprice.toFixed(2)}</i></div>
    <p>评论：0条 <span>收藏：0</span></p>
    <div class="count-buy">
      <span>购买数量：</span>
        <button type="button">-</button>
        <input type="number" required min="1" name="scount" value="1"/>
        <button type="button">+</button>
    </div>
    <button type="button" class="btn1" title="${d.pid}">
      <span class="glyphicon glyphicon-shopping-cart"></span>
      加入购物车
    </button>
    <button type="button" class="btn2" title="${d.pid}">
      立即购买
    </button>`;
              $('div#details').html(html);
          }


      })
  });
  $('div#details').on('click','div.right>div.count-buy>button',function(){
    if($(this).html()=="+"){
      var n=parseFloat($(this).prev().val());
      n++;
      $(this).prev().val(n);
    }else if($(this).html()=="-"){
      var n=parseFloat($(this).next().val());
      n--;
      n==0&&(n=1);
      $(this).next().val(n);
    }
  });


  $('div#details').on('click','div.right button.btn1',function(){
    if(sessionStorage['loginUid']==undefined){
      $("#login").show();
    }else{
        var uid=sessionStorage['loginUid'];
        var pid=$(this).attr('title');
        var scount=$('#details .right>div.count-buy>input').val();
        console.log(uid,pid,scount);
        $.ajax({
          type:'POST',
          url:'/add_shoppingCart',
          data:{pid:pid,uid:uid,count:scount},
          success:function(data){
            console.log(data);
            //document.location.reload();
            var m=$('#rightFixed li.sc .badge').html()||0;
            console.log(m);
               // m=parseFloat($('#rightFixed li.sc .badge').html());
            m=parseFloat(m);scount=parseFloat(scount);
            m+=scount;
            console.log(m);
            $('#rightFixed li.sc .badge').html(m);
            if(confirm('添加购物车成功！您的购物车有 '+m+' 件商品，去购物车结算?')){
              location.href='shoppingCart.html';
            }
          }
        })

      }


  });

  $('div#details').on('click','div.right button.btn2',function(){
    //if(sessionStorage['loginUid']==undefined){
    //  $("#login").show();
    //}else{
    //  var uid=sessionStorage['uid'];
    //  sessionStorage['pic']=$('#details .left>p>img').attr('src');
    //  var pid=$(this).attr('title');
    //  sessionStorage['pid']=pid;
    //  sessionStorage['pname']=$('div.right>h3').html();
    //  sessionStorage['price']=$('div.right .price b').html().slice(1);
    //  var scount=$('#details .right>div.count-buy>input').val();
    //  sessionStorage['scount']=scount;
    //  console.log(pid,scount);
    //  location.href='order.html';
    //}

    if(sessionStorage['loginUid']==undefined){
      $("#login").show();
    }else{
      var arr=[];
          arr.push({
            pid:$(this).parents('.right').prev().find('img').attr('alt'),
            pic:$(this).parents('.right').prev().find('img').attr('src'),
            count:$(this).parent().find('input').val(),
            price:$(this).parent().find('.price b').html().slice(1),
            pname:$(this).parent().find('h3').html()
          });
      var str=JSON.stringify(arr);
      sessionStorage['orderDetails']=str;
      location.href='order.html';
    }
  })
});/**
 * Created by zhouli on 2017/5/29.
 */















