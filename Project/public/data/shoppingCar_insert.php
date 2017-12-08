<?php
 @$product=$_REQUEST['product'] or die("请选择商品名称！");
 $price=$_REQUEST['price'];
 $pic=$_REQUEST['pic'];
 @$scount=$_REQUEST['scount'] or die("请选择商品数量！");
 $conn=mysqli_connect('127.0.0.1','root','','myitem');
 mysqli_query($conn,"set names utf8");
 $sql="INSERT INTO t_shoppingcar VALUES(null,'$pic','$product',$price,$scount)";
 $result=mysqli_query($conn,$sql);
 if($result===true){
  echo "加入购物车成功！";
 }else{
  echo "商品添加失败！";
 }
?>