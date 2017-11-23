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

app.get('/login',(req,res)=>{
    var uname = req.query.uname;
    var pwd = req.query.pwd;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT * FROM manager WHERE inviteCode=? and password = ? and status = 0',[uname,pwd],(err,result)=>{
                if(result!=null){
                    result[0]['loginInfo']={msg:"登录成功！",status:1};
                    res.json(result[0]);
                }
            })
        }
    })
});

//获取代理信息
app.get('/getAgentInfo',(req,res)=>{
    var managerId=req.query.managerId;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.id=? and m.id = a.managerId',[managerId],(err,result)=>{
                //console.log(result);
                res.json(result[0]);
            })
        }
        conn.release();
    })
});

//获取代理
app.get('/getManagers',(req,res)=>{
    var managerId=req.query.managerId;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId',[managerId],(err,result)=>{
                //console.log(result);
                if(result!=null){
                    var progress=0;
                    var progress2=0;
                    var progress3=0;
                    for(let manager of result){
                        conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? ',[manager.id],(err,sum)=>{

                           if(sum[0].m){
                               manager['sumMoney']=sum[0].m;
                           }else{
                               manager['sumMoney']=0;
                           }
                            progress++;
                            if(progress===result.length&&progress2===result.length&&progress3===result.length){
                                //console.log(result);
                                res.json(result);
                                conn.release();
                            }
                        });
                        conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id',[manager.id],(err,count)=>{

                            manager['accountNumber']=count[0].cou;
                            progress2++;
                            if(progress===result.length&&progress2===result.length&&progress3===result.length){
                                //console.log(result);
                                res.json(result);
                                conn.release();
                            }
                        });
                        conn.query('select count(id) as cou from manager  where  manager_up_id=?',[manager.id],(err,count)=>{

                            manager['agentNumber']=count[0].cou;
                            progress3++;
                            if(progress===result.length&&progress2===result.length&&progress2===result.length){
                                //console.log(result);
                                res.json(result);
                                conn.release();
                            }
                        })

                    }
                }
            })
        }
    })
});

//app.get('/getManagers',(req,res)=>{
//    var managerId=req.query.managerId;
//    var startTime='1970-01-01';
//    var endTime='2017-11-23';
//    pool.getConnection((err,conn)=>{
//        if(err){
//            console.log(err);
//        }else{
//            conn.query("select m.*,IFNULL(sum(n.money),0) as actualCard from (select b.id, b.power_id, b.name, b.telephone, b.manager_up_id, b.status,b.inviteCode,b.weixin,b.qq,b.rootManager,b.rebate,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as levelStr,IFNULL(count(a.id),0) as totalCards,b.uuid,b.createTime from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>2) m left join  (select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime > ?    and a.payTime < ?  and  b.pid=?  and (a.gameId = 1 or a.gameId = 3)  and payType = 0 group by b.id having b.id>2 ) n  on n.levelStr like m.levelStr group by m.id ORDER BY actualCard desc,totalCards desc",[startTime,endTime,1],(err,result)=>{
//                console.log(result);
//                res.json(result);
//                conn.release();
//                //and a.payTime > ?    and a.payTime < ?  and  b.pid=?
//            })
//        }
//
//    })
//});

//获取我的会员
app.get('/getAccounts',(req,res)=>{
    var managerId=req.query.managerId;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id order by a.createTime desc',[managerId],(err,result)=>{
                //console.log(result);
                res.json(result);
                conn.release();
            })
        }

    })
});

//获取账单明细
app.get('/getDetails',(req,res)=>{
    var managerId=req.query.managerId;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT p.* from paylog p WHERE p.managerId=?  order by payTime desc',[managerId],(err,paylogs)=>{
                var progress=0;
                for(let paylog of paylogs){
                    conn.query('SELECT m.inviteCode,m.name,m.power_id,m.rebate,a.Uuid as muuid FROM manager m,account a WHERE m.id=? and a.managerId = m.id',[paylog.managerId],(err,mana)=>{
                        paylog['inviteCode']=mana[0].inviteCode;
                        paylog['name']=mana[0].name;
                        paylog['power_id']=mana[0].power_id;
                        paylog['rebate']=mana[0].rebate;
                        paylog['muuid']=mana[0].muuid;
                        progress++;
                        if(progress===paylogs.length){
                            //console.log(result);
                            res.json(paylogs);
                            conn.release();
                        }
                    })
                }
            })
        }

    })
});

