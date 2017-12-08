/**
 * Created by bjwsl-001 on 2017/6/3.
 */
$(function(){
    var data=sessionStorage['loginUid'];
    $.ajax({
      type:'GET',
      data:{uid:data},
      url:'/shoppingCart-list',
      success:function(data){
        //console.log(data);
        var html=`<table width="100%">
       <thead>
         <tr>
           <th>名称</th>
           <th>价格</th>
           <th>数量</th>
           <th>小计</th>
           <th>操作</th>
         </tr>
       </thead>
       <tbody>
       `;
        for(var i=0,arr=[];i<data.length;i++){
          var o=data[i];
          html+=`<tr>
           <td>
               <input type="checkbox" checked/>
               <img src="${o.pic}" style="width:120px" alt="${o.pid}"/>
               <a href="#">${o.pname}</a>
           </td>
           <td class="price">￥${o.price.toFixed(2)}</td>
           <td class="product-count">
             <button type="button" title="${o.sid}">-</button><span>${o.scount}</span><button title="${o.sid}" type="button">+</button>
           </td>
           <td class="subtotal">￥${(o.price*o.scount).toFixed(2)}
           </td>
           <td>
             <a href="${o.sid}"  class="del-btn">删除</a>
           </td>
         </tr>
         `;

          arr.push(o.price*o.scount);
        }
       function sum(arr){
         for(var i=0,sum=0;i<arr.length;i++){
           sum+=arr[i];
         }
         return sum;
       }
       html+=`</tbody>
     </table>
     <p>
      <label class="left"><input type="checkbox" id="checkAll" checked/>全选</label>
      <span class="total">总计：<b>￥${sum(arr).toFixed(2)}</b></span>
    </p>
    <br/><br/>
    <p>
      <a class="btn btn-default">继续购物</a><a class="btn btn-default">结算订单</a>
    </p>`;
        $("#cart-details").html(html);
      }
    });
    $("#cart-details").on('click','#checkAll',function(){
        if(this.checked){
            $("#cart-details table td input").prop('checked',true);
            var arr1=[];
            $.each($("#cart-details table .subtotal"),function(i,dom){
                arr1.push(parseFloat($(dom).html().slice(1)));
            });
            //arr1.push(parseFloat($("#cart-details table .subtotal").html().slice(1)));
            var sum=arr1.reduce(function(prev,val){
                return prev+val;
            });
            console.log(arr1,sum);
            $("#cart-details .total b").html('￥'+sum.toFixed(2));
        }else{
            $("#cart-details table td input").prop('checked',false);
            $("#cart-details .total b").html('￥0.00');
        }
    });
    $("#cart-details").on('click','table td input',function(){
        var p=parseFloat($(this).parents('tr').find('.subtotal').html().slice(1));
        var before=parseFloat($("#cart-details .total b").html().slice(1));
        if(!this.checked){
            var after='￥'+(before-p).toFixed(2);
            $("#cart-details #checkAll").prop('checked',false);
        }else {
            var after='￥'+(before+p).toFixed(2);
            if($('#cart-details table td input:not(:checked)').length==0){
                $("#cart-details #checkAll").prop('checked',true);
            }
        }
        $("#cart-details .total b").html(after);
    });

  $("#cart-details").on('click','.product-count button',function(){
    if($(this).html()=='+'){
      var n=parseFloat($(this).prev().html());
      n++;
      $(this).prev().html(n);
      var m=parseFloat($('#rightFixed li.sc .badge').html());
      m++;
      $('#rightFixed li.sc .badge').html(m);
        var price = parseFloat($(this).parent().prev().html().slice(1));
       // console.log(typeof price, price, typeof n, n);
        var h = '￥' + (price * n).toFixed(2);
        $(this).parent().next().html(h);
        if($(this).parents('tr').find('input').prop('checked')) {
            var tot = (parseFloat($(".total>b").html().slice(1)) + price).toFixed(2);
            $(".total>b").html("￥" + tot);
            $(".pay>b").html("￥" + tot);
        }

      var data=$(this).attr('title');
      $.ajax({
        url:'/add_count',
        data:{sid:data},
        success:function(data){
          alert(data.msg);
        }
      })
    }else if($(this).html()=='-'){
      var n=parseFloat($(this).next().html());
      n--;
      if(n<=0){
        n=1;
        return;
      }
      $(this).next().html(n);
      var m=parseFloat($('#rightFixed li.sc .badge').html());
      m--;
      $('#rightFixed li.sc .badge').html(m);
        var price=parseFloat($(this).parent().prev().html().slice(1));
        //console.log(typeof price,price,typeof n,n);
        var h='￥'+(price*n).toFixed(2);
        $(this).parent().next().html(h);
        if($(this).parents('tr').find('input').prop('checked')){
            var tot=(parseFloat($(".total>b").html().slice(1))-price).toFixed(2);
            $(".total>b").html("￥"+tot);
            $(".pay>b").html("￥"+tot);
        }

      var data=$(this).attr('title');
      $.ajax({
        url:'/min_count',
        data:{sid:data},
        success:function(data){
          alert(data.msg);
        }
      })
    }
  });
  $("#cart-details").on('click','table a.del-btn',function(e){
    e.preventDefault();
    var sid=$(this).attr('href');
    var subt=$(this).parent().prev().html().slice(1);
    var total=(parseFloat($(".total>b").html().slice(1))-subt).toFixed(2);
    $(".total>b").html('￥'+total);
    $(".pay>b").html("￥"+total);
    var n=$(this).parent().prev().prev().children('span').html();
    var m=$('#rightFixed li.sc .badge').html();
    $('#rightFixed li.sc .badge').html(m-n);
    $.ajax({
      url:'/delete-shoppingCart',
      data:{sid:sid},
      success:function(data){
        alert(data.msg);
      }
    });
    $(this).parent().parent().remove();
  });

    $("#cart-details").on('click','p>a:first',function(e){
        e.preventDefault();
        location.href='index.html';
    });

    $("#cart-details").on('click','p>a:last',function(e){
        e.preventDefault();
        if(sessionStorage['loginUid']==undefined){
            $("#login").show();
        }else{
            var arr=[];
            $.each($(this).parent().parent().find('table tbody tr'),function(i,dom){
                if($(dom).find('input').prop('checked')){
                    arr.push({
                        pid:$(dom).find('img').attr('alt'),
                        pic:$(dom).find('img').attr('src'),
                        count:$(dom).find('.product-count span').html(),
                        price:$(dom).find('.price').html().slice(1),
                        pname:$(dom).find('td:first a').html()
                    });

                }
            });
            var str=JSON.stringify(arr);
            sessionStorage['orderDetails']=str;
            location.href='order.html';
        }
    })


});