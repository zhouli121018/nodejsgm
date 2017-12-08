<?php
header("content-type:application/json;charset=utf-8");
@$uname=$_REQUEST['uname'] or die('{"code"：-1,"msg":"请输入用户名！"}');
@$upwd=$_REQUEST['upwd'] or die('{"code"：-2,"msg":"请输入密码！"}');
$conn=mysqli_connect('127.0.0.1','root','','myitem');
mysqli_query($conn,"set names utf8");
$sql="select * from t_user where uname='$uname'";
$result=mysqli_query($conn,$sql);
$row=mysqli_fetch_row($result);
if($row===null){
	$sql="INSERT INTO t_user VALUES(null,'$uname','upwd',now())";
	mysqli_query($conn,$sql);
	echo '{"code":1,"msg":"注册成功！"}'
}else{
    echo '{"code"：-3,"msg":"注册失败！"}';
}
?>