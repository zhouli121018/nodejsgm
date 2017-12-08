/**
 * Created by bjwsl-001 on 2017/6/9.
 */
$(function(){
  //var html=`<img src="${sessionStorage['pic']}" width="120px" height="80px"/> ${sessionStorage['pname']}`;
  //$('table tr>td:eq(0)').html(html);
  //$('table tr>td:eq(1)').html('￥'+sessionStorage['price']);
  //$('table tr>td:eq(2)').html(sessionStorage['scount']);
  //var subtotal=parseFloat(sessionStorage['price']*sessionStorage['scount']);
  //$('table tr>td:eq(3)').html('￥'+subtotal.toFixed(2));
  //$('div.order-msg>p:eq(0) b').html('￥'+subtotal.toFixed(2));
  //$('div.order-msg>p.pay b').html('￥'+(subtotal+5).toFixed(2));
  //$('div.send-method input').click(function(){
  //  var cost=parseFloat($(this).val());
  //  $('div.order-msg>p:eq(1) b').html('￥'+cost.toFixed(2));
  //  $('div.order-msg>p.pay b').html('￥'+(subtotal+cost).toFixed(2))
  //})
 var html1=`<tr>
        <td><img src="img1/1.jpg" alt="1"/>蔓越莓100x2袋</td>
        <td>￥45.00</td>
        <td>1</td>
        <td>￥45.00</td>
      </tr>`;
  var arr=JSON.parse(sessionStorage['orderDetails']);
  console.log(arr);
  var sum=0;
  for(var i=0,html='';i<arr.length;i++){
    var o=arr[i];
    sum += o.price*o.count;
    html+=`<tr class="dtl">
        <td><input type="checkbox" class="subCheck" checked/><img src="${o.pic}" alt="${o.pid}" />${o.pname}</td>
        <td>￥${parseFloat(o.price).toFixed(2)}</td>
        <td class="cot">${o.count}</td>
        <td>￥${parseFloat(o.price*o.count).toFixed(2)}</td>
      </tr>`;
  }
  html+=`<tr><td  colspan="2"><input class="all" type="checkbox" checked/>全选</td><td>总计：</td><td class="total">￥${sum.toFixed(2)}</td></tr>`
  $("#tbd").html(html);
  $('div.order-msg>p.pay b').html('￥'+(sum+5).toFixed(2));
  $('#tbd').on('click','input.all',function(){
    if(this.checked){
      var cost=parseFloat($('div.send-method input:checked').val());
      $('div.order-msg>p:eq(0) b').html('￥'+cost.toFixed(2));
      $(this).parents('table').find('.subCheck').prop('checked',true);
      $("#tbd .total").html('￥'+sum.toFixed(2));
      $('div.order-msg>p.pay b').html('￥'+(sum+5).toFixed(2));
    }else{
      $(this).parents('table').find('.subCheck').prop('checked',false);
      $("#tbd .total").html('￥0.00');
      $('div.order-msg>p.pay b').html('￥0.00');
      $('div.order-msg>p:eq(0) b').html('￥0.00');

    }
  });
  $("#tbd").on('click','.subCheck',function(){
    var before=parseFloat($('#tbd .total').html().slice(1));
    var price=parseFloat($(this).parent().next().html().slice(1));
    var beforePay=parseFloat($('div.order-msg>p.pay b').html().slice(1));
    if(!this.checked){
      $("#tbd .all").prop('checked',false);
      var after='￥'+(before-price).toFixed(2);
      $("#tbd .total").html(after);
      var afterPay='￥'+(beforePay-price).toFixed(2);
      $('div.order-msg>p.pay b').html(afterPay)

    }else{
      if($('#tbd  input.subCheck:not(:checked)').length==0){
        $("#tbd .all").prop('checked',true);
      }
      var after='￥'+(before+price).toFixed(2);
      $("#tbd .total").html(after);
      var afterPay='￥'+(beforePay+price).toFixed(2);
      $('div.order-msg>p.pay b').html(afterPay);
    }
  });
  $('div.send-method input').click(function(){
    var cost=parseFloat($(this).val());
    var tot=parseFloat($("#tbd .total").html().slice(1));
    $('div.order-msg>p:eq(0) b').html('￥'+cost.toFixed(2));
    $('div.order-msg>p.pay b').html('￥'+(tot+cost).toFixed(2));
  });


  $('.order-msg .sbm').click(function(){
    if($('.order-msg #uname').val().length==0){
      alert('请填写收件人信息');
      $('#uname').focus();
    }else if($('#tbd .subCheck:checked').length==0){
      alert('请选择要购买的商品')
    }else{
      var rcvname=$('#uname').val();
      var uid=sessionStorage['loginUid'];
      var price=$('div.order-msg>p.pay b').html().slice(1);
      var payment=$('.order-msg .payment input').val();
      var orderDetails=[];
      $.each($("#tbd tr:not(:last-child)"),function(i,dom){
        if($(dom).find('.subCheck').prop('checked')){
          orderDetails.push({
            pid:$(dom).find('img').attr('alt'),
            count:$(dom).find('.cot').html()
          })
        }
      });
      //console.log(orderDetails);
      var str=JSON.stringify(orderDetails);
      $.ajax({
        type:'POST',
        url:'/submitOrder',
        data:{
          rcvname:rcvname,
          uid:uid,
          price:price,
          payment:payment,
          orderDetails:str
        },
        success:function(data){
          console.log(data);
          if(confirm('下单成功！订单编号：'+data.oid +'\;去用户中心查看订单信息？')){
            location.href='usercenter.html';
          }
        }
      })
    }

  })

});