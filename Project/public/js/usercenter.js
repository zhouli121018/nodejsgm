/**
 * Created by bjwsl-001 on 2017/6/5.
 */
$(function(){
  $('#usercenter>ul>li a').click(function(e){
    e.preventDefault();
    $(this).parent().addClass('active').siblings().removeClass('active');
    var id=$(this).attr('href');
    $(id).show().siblings().hide();
  });
  var data=sessionStorage['loginUid'];
  $.ajax({
    type:'GET',
    data:{
      uid:data
    },
    url:'/order/list',
    success:function(data){
      console.log(data);
      if(data.length==0){
        $("#orderList").html('<h3>您还没有下单，再逛逛吧...</h3>');
      }else{
        var html=`<table border="1" style="width:100%">
          <thead>
          <tr>
            <th>订单信息</th>
            <th>收货人</th>
            <th>订单金额</th>
            <th>订单时间</th>
            <th>订单状态</th>
            <th>操作</th>
          </tr>
          </thead>
          <tbody>`;
        for(var i=data.length-1;i>=0;i--){
          var o=data[i];
          html+=`
          <tr>
            <td colspan="6"><input type="checkbox"/> <b>订单编号：${o.oid}</b></td>
          </tr>
          <tr>
            <td>`;
          for(var j=0;j<o.productList.length;j++){
            var p=o.productList[j];
            html+=`<img src="${p.pic}" style="width:120px;height:100px">`;
          }
          html+= `</td>
            <td>${o.rcvName}</td>
            <td>￥${o.price}<br>${o.payment===1?'货到付款':(o.payment===2?'支付宝支付':'微信支付')}</td>
            <td>${new Date(o.orderTime).toLocaleDateString() }<br/>${new Date(o.orderTime).toLocaleTimeString()}</td>
            <td>${o.status==1?'备货中':(o.status==2?'运输中':'已签收')}</td>
            <td>
              <a href="#">查看</a><br/>
              <a href="#">评价</a>
            </td>
          </tr>`;
        }
        html+=` </tbody></table>`;
        $("#orderList").html(html);
      }
    }
  });

  $.ajax({
    type: 'GET',
    url: '/order/buystat',
    data: {uid: sessionStorage['loginUid']},
    success: function(list){
      console.log(list);//异步请求到了消费统计数据
      //创建一个图表对象
      var c = new FusionCharts({
        type: 'line',//'doughnut3d',//'doughnut2d',//'pie3d',//'pie2d',//'line',//'bar3d',//'bar2d',//'column3d',//'column2d',
        renderAt: 'buyCountSvg',
        width: 800,
        height: 400,
        dataSource: {
          data: list    //[{label:x, value:x}]
        }
      });
      //渲染出来
      c.render();
    }
  });

  $('#buyCount ul li a').click(function(e){
    e.preventDefault();
    $(this).parent().addClass('active').siblings().removeClass('active');
    var that=this;
    $.ajax({
      type: 'GET',
      url: '/order/buystat',
      data: {uid: sessionStorage['loginUid']},
      success: function(list){
        console.log(list);//异步请求到了消费统计数据
        //创建一个图表对象
        var type=$(that).attr('href');
        console.log(type);
        var c = new FusionCharts({
          type: type,//'doughnut3d',//'doughnut2d',//'pie3d',//'pie2d',//'line',//'bar3d',//'bar2d',//'column3d',//'column2d',
          renderAt: 'buyCountSvg',
          width: 800,
          height: 400,
          dataSource: {
            data: list    //[{label:x, value:x}]
          }
        });
        //渲染出来
        c.render();
      }
    });

    //e.preventDefault();
    //$(this).parent().addClass('active').siblings().removeClass('active');
    //var that=this;
    //var list=  [
    //  {label: '6月', value: 3500},
    //  {label: '7月', value: 2500},
    //  {label: '8月', value: 5000},
    //  {label: '9月', value: 4000},
    //  {label: '10月', value: 500},
    //  {label: '11月', value: 5500},
    //  {label: '12月', value: 7000},
    //  {label: '1月', value: 3000},
    //  {label: '2月', value: 4000},
    //  {label: '3月', value: 5000},
    //  {label: '4月', value: 3800},
    //  {label: '5月', value: 4300}
    //];
    //    var type=$(that).attr('href');
    //    console.log(type);
    //    var c = new FusionCharts({
    //      type: type,//'doughnut3d',//'doughnut2d',//'pie3d',//'pie2d',//'line',//'bar3d',//'bar2d',//'column3d',//'column2d',
    //      renderAt: 'buyCountSvg',
    //      width: 800,
    //      height: 400,
    //      dataSource: {
    //        data: list    //[{label:x, value:x}]
    //      }
    //    });
    //    //渲染出来
    //    c.render();



  })
});