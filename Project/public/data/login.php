<?php
@$uname=$_REQUEST['uname'] or die('{"code"：-1,"msg":"请输入用户名！"}';);
@$upwd=$_REQUEST['upwd'] or die('{"code"：-2,"msg":"请输入密码！"}';);
$conn=mysqli_connect('127.0.0.1','root','','myitem');
mysqli_query($conn,"set names utf8");
$sql="select uid,uname,upwd from t_user where uname='$uname' and upwd='$upwd'";
$result=mysqli_query($conn,$sql);
$row=mysqli_fetch_assoc($result);
$arr=["code"=>1,"uid"=>$row['uid'],"uname"=>$row['uname']]
if($row===null){
 echo '{"code"：-3,"msg":"登录失败！"}';
}else{
 echo json_encode($arr);
}
?>