<?php
$sid=$_REQUEST['sid'];
$conn=mysqli_connect('127.0.0.1','root','','myitem');
mysqli_query($conn,"set names utf8");
$sql="DELETE FROM t_shoppingCar WHERE sid= $sid";
$result=mysqli_query($conn,$sql);
if($result===true){
  echo "删除成功！";
}else{
  echo "删除失败！";
}
?>