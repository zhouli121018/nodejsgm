<?php
$conn=mysqli_connect('127.0.0.1','root','','myitem');
mysqli_query($conn,"set names utf8");
$sql="SELECT * FROM t_shoppingCar";
$result=mysqli_query($conn,$sql);
$rows=mysqli_fetch_all($result,MYSQLI_ASSOC);
 echo "<table style="width:85%;margin:0 auto;border-collapse:collapse;">";
  echo "<tr>";
  echo "<th>图片</th>";
  echo "<th>商品名称</th>";
  echo "<th>单价</th>";
  echo "<th>数量</th>";
  echo "<th>小计</th>";
  echo "<th>编辑</th>";
  echo "</tr>";
foreach($rows as $k=>$v){
   echo "<tr>";
   echo "<td><img src='$v[pic]' alt='$v[pic]' /></td>";
   echo "<td>$v[product]</td>";
   echo "<td>$v[price]</td>";
   echo "<td>$v[scount]</td>";
   echo "<td>($v[scount]*$v[price])</td>";
   echo "<td><a href='$v[sid]' class="btn-delete">删除</a></td>";
   echo "</tr>";
}
  echo "</table>";
if($result===true){
  echo "删除成功！";
}else{
  echo "删除失败！";
}
?>