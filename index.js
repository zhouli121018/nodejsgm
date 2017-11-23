/**
 * Created by 51216 on 2017/11/22.
 */
const http=require('http');
const express=require('express');
const mysql=require('mysql');
const qs=require('querystring');
var pool=mysql.createPool({
    host:'120.76.100.224',
    user:'mahjong',
    password:'a257joker',
    database:'mahjong_hbe',
    connectionLimit:10
});
var app=express();
var server=http.createServer(app);
server.listen(8081);
app.use(express.static('./public'));

//获取代理信息
app.get('/getAgentInfo',(req,res)=>{
    var managerId=req.query.managerId;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT m.*,a.uuid,a.nickName FROM manager m,account a WHERE m.id=? and m.id = a.managerId',[managerId],(err,result)=>{
                console.log(result);
                if(result!=null){
                    res.json(result[0]);
                }
            })
        }
        conn.release();
    })
});

app.get('/getManagers',(req,res)=>{
    var managerId=req.query.managerId;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT m.*,a.uuid,a.nickName FROM manager m,account a WHERE m.id=? and m.id = a.managerId',[managerId],(err,result)=>{
                console.log(result);
                if(result!=null){
                    res.json(result[0]);
                }
            })
        }
        conn.release();
    })
});


