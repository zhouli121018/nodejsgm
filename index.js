/**
 * Created by 51216 on 2017/11/22.
 */
const http=require('http');
const express=require('express');
const mysql=require('mysql');
const qs=require('querystring');
const fs   = require("fs");
var cookieParser = require('cookie-parser');
var session = require('express-session');
var pool=mysql.createPool({
    host:'127.0.0.1',
    //user:'root',//mahjong
    //password:'123456',//a257joker
    user:'mahjong',
    password:'a257joker',
    database:'mahjong_hbe',
    connectionLimit:10
});
var app=express();
var server=http.createServer(app);
server.listen(8082);
app.use(express.static('./public'));
app.use(cookieParser('sessiontest'));
app.use(session({
    secret: 'sessiontest',//与cookieParser中的一致
    resave: true,
    saveUninitialized:true
}));

app.get('/login',(req,res)=>{
    var uname = req.query.uname;
    var pwd = req.query.pwd;
    if(req.session.user){
        var user=req.session.user;
        if(uname==user.inviteCode&&pwd==user.password){
            res.json(user);
        }else{
            login();
        }
    }else{
        login();
    }
    function login(){
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM manager WHERE inviteCode=? and password = ? and status = 0',[uname,pwd],(err,result)=>{

                    if(result.length==0){
                        result.push({msg:'用户名或密码不正确！',logStatus:0});
                    }else{
                        result[0]['msg']='登录成功！';
                        result[0]['logStatus']=1;
                        req.session.user=result[0];
                    }
                    console.log(result);
                    res.json(result[0]);

                    //res.json({msg:'用户名或密码不正确！',status:0});

                    conn.release();
                })
            }
        })
    }

});

app.get('/logout',(req,res)=>{
    console.log("++++"+req.session.user);
    req.session.destroy();
});

//刷新
app.get('/refresh',(req,res)=>{
    if(req.session.user){
        res.json({"status":1});
    }else{
        res.json({"status":0});
    }
});

//获取代理信息
app.get('/getAgentInfo',(req,res)=>{
    if(req.session.user){
        var user=req.session.user;
        var managerId=user.id;
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
    }
});

//获取代理
app.get('/getChildAgents',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = req.query.managerId;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId', [managerId], (err, result)=> {
                    //console.log(result);
                    if (result != null) {
                        var progress = 0;
                        var progress2 = 0;
                        var progress3 = 0;
                        for (let manager of result) {
                            conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? ', [manager.id], (err, sum)=> {

                                if (sum[0].m) {
                                    manager['sumMoney'] = sum[0].m;
                                } else {
                                    manager['sumMoney'] = 0;
                                }
                                progress++;
                                if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                            conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id', [manager.id], (err, count)=> {

                                manager['accountNumber'] = count[0].cou;
                                progress2++;
                                if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                            conn.query('select count(id) as cou from manager  where  manager_up_id=?', [manager.id], (err, count)=> {

                                manager['agentNumber'] = count[0].cou;
                                progress3++;
                                if (progress === result.length && progress2 === result.length && progress2 === result.length) {
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
    }
});
app.get('/getManagers',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId', [managerId], (err, result)=> {
                    //console.log(result);
                    if (result.length>0) {
                        var progress = 0;
                        var progress2 = 0;
                        var progress3 = 0;
                        for (let manager of result) {
                            conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? ', [manager.id], (err, sum)=> {

                                if (sum[0].m) {
                                    manager['sumMoney'] = sum[0].m;
                                } else {
                                    manager['sumMoney'] = 0;
                                }
                                progress++;
                                if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                            conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id', [manager.id], (err, count)=> {

                                manager['accountNumber'] = count[0].cou;
                                progress2++;
                                if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                            conn.query('select count(id) as cou from manager  where  manager_up_id=?', [manager.id], (err, count)=> {

                                manager['agentNumber'] = count[0].cou;
                                progress3++;
                                if (progress === result.length && progress2 === result.length && progress2 === result.length) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            })

                        }
                    }else{
                        res.json({"agents":0});
                        conn.release();
                    }
                })
            }
        })
    }
});

//根据时间等条件查询代理数据
app.get('/searchAgents',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var starttime=req.query.starttime;
        var endtime=req.query.endtime;
        var now=new Date();
        now.setDate(now.getDate()+1);
        var overArr=now.toLocaleDateString().split('/');
        for(var i=0;i<overArr.length;i++){
            if(overArr[i]<10){
                overArr[i]=0+overArr[i];
            }
        }
        var overTime=overArr.join('-');
        console.log(overTime);
        if(!starttime){
            starttime='1970-01-01';
        }
        if(!endtime){
            endtime=overTime;
        }
        var uname=req.query.uname;
        var inviteCode=req.query.invitecode;
        console.log(starttime,endtime,uname,inviteCode);
        if(!uname&&!inviteCode){
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId', [managerId], (err, result)=> {
                        //console.log(result);
                        if (result.length>0) {
                            var progress = 0;
                            var progress2 = 0;
                            var progress3 = 0;
                            for (let manager of result) {
                                conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? and p.payTime BETWEEN ? AND ?', [manager.id,starttime,endtime], (err, sum)=> {

                                    if (sum[0].m) {
                                        manager['sumMoney'] = sum[0].m;
                                    } else {
                                        manager['sumMoney'] = 0;
                                    }
                                    progress++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id', [manager.id], (err, count)=> {

                                    manager['accountNumber'] = count[0].cou;
                                    progress2++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(id) as cou from manager  where  manager_up_id=?', [manager.id], (err, count)=> {

                                    manager['agentNumber'] = count[0].cou;
                                    progress3++;
                                    if (progress === result.length && progress2 === result.length && progress2 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                })

                            }
                        }else{
                            res.json([]);
                            conn.release();
                        }
                    })
                }
            })
        }else if(uname&&inviteCode){
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId and m.name=? and m.inviteCode=?', [managerId,uname,inviteCode], (err, result)=> {
                        console.log("---::"+result);
                        if (result.length>0) {
                            var progress = 0;
                            var progress2 = 0;
                            var progress3 = 0;
                            for (let manager of result) {
                                conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? and p.payTime BETWEEN ? AND ?', [manager.id,starttime,endtime], (err, sum)=> {

                                    if (sum[0].m) {
                                        manager['sumMoney'] = sum[0].m;
                                    } else {
                                        manager['sumMoney'] = 0;
                                    }
                                    progress++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id', [manager.id], (err, count)=> {

                                    manager['accountNumber'] = count[0].cou;
                                    progress2++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(id) as cou from manager  where  manager_up_id=?', [manager.id], (err, count)=> {

                                    manager['agentNumber'] = count[0].cou;
                                    progress3++;
                                    if (progress === result.length && progress2 === result.length && progress2 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                })

                            }
                        }else{
                            console.log('else');
                            res.json([]);
                            conn.release();
                        }
                    })
                }
            })
        }else if(uname&&!inviteCode){
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId and m.name=? ', [managerId,uname], (err, result)=> {
                        //console.log(result);
                        if (result.length>0) {
                            var progress = 0;
                            var progress2 = 0;
                            var progress3 = 0;
                            for (let manager of result) {
                                conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? and p.payTime BETWEEN ? AND ?', [manager.id,starttime,endtime], (err, sum)=> {

                                    if (sum[0].m) {
                                        manager['sumMoney'] = sum[0].m;
                                    } else {
                                        manager['sumMoney'] = 0;
                                    }
                                    progress++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id', [manager.id], (err, count)=> {

                                    manager['accountNumber'] = count[0].cou;
                                    progress2++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(id) as cou from manager  where  manager_up_id=?', [manager.id], (err, count)=> {

                                    manager['agentNumber'] = count[0].cou;
                                    progress3++;
                                    if (progress === result.length && progress2 === result.length && progress2 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                })

                            }
                        }else{
                            res.json([]);
                            conn.release();
                        }
                    })
                }
            })
        }else if(inviteCode&&!uname){
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId and m.inviteCode=?', [managerId,inviteCode], (err, result)=> {
                        //console.log(result);
                        if (result.length>0) {
                            var progress = 0;
                            var progress2 = 0;
                            var progress3 = 0;
                            for (let manager of result) {
                                conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.managerId =? and p.payTime BETWEEN ? AND ?', [manager.id,starttime,endtime], (err, sum)=> {

                                    if (sum[0].m) {
                                        manager['sumMoney'] = sum[0].m;
                                    } else {
                                        manager['sumMoney'] = 0;
                                    }
                                    progress++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(a.id) as cou from account a,manager g where  a.manager_up_id=? and g.id=a.manager_up_id', [manager.id], (err, count)=> {

                                    manager['accountNumber'] = count[0].cou;
                                    progress2++;
                                    if (progress === result.length && progress2 === result.length && progress3 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(id) as cou from manager  where  manager_up_id=?', [manager.id], (err, count)=> {

                                    manager['agentNumber'] = count[0].cou;
                                    progress3++;
                                    if (progress === result.length && progress2 === result.length && progress2 === result.length) {
                                        //console.log(result);
                                        res.json(result);
                                        conn.release();
                                    }
                                })

                            }
                        }else{
                            res.json([]);
                            conn.release();
                        }
                    })
                }
            })
        }

    }
});
//app.get('/getManagers',(req,res)=>{
//    if(req.session.user) {
//        var user = req.session.user;
//        var managerId = user.id;
//        var startTime = '1970-01-01';
//        var endTime = '2017-11-23';
//        pool.getConnection((err, conn)=> {
//            if (err) {
//                console.log(err);
//            } else {
//                conn.query("select m.*,IFNULL(sum(n.money),0) as actualCard from (select b.id, b.power_id, b.name, b.telephone, b.manager_up_id, b.status,b.inviteCode,b.weixin,b.qq,b.rootManager,b.rebate,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as levelStr,IFNULL(count(a.id),0) as totalCards,b.uuid,b.createTime from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>2) m left join  (select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime > ?    and a.payTime < ?  and  b.pid=?  and (a.gameId = 1 or a.gameId = 3)  and payType = 0 group by b.id having b.id>2 ) n  on n.levelStr like m.levelStr group by m.id ORDER BY actualCard desc,totalCards desc", [startTime, endTime, 1], (err, result)=> {
//                    console.log(result);
//                    var result0=[];
//                    for(var i=0;i<result.length;i++){
//                        if(result[i].id==managerId){
//                            result0=result[i];
//                            break;
//                        }else{
//                            result[i].a
//                        }
//
//                    }
//                    res.json(result);
//                    conn.release();
//                    //and a.payTime > ?    and a.payTime < ?  and  b.pid=?
//                })
//            }
//
//        })
//    }
//});

//获取我的会员
app.get('/getAccounts',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id order by a.createTime desc', [managerId], (err, result)=> {
                    //console.log(result);
                    if(result.length>0){
                        var progress=0;
                        for(let account of result){
                            conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =?', [account.uuid], (err, sum)=> {
                                console.log(sum);
                                if (sum[0].m) {
                                    account['sumMoney'] = sum[0].m;
                                } else {
                                    account['sumMoney'] = 0;
                                }
                                progress++;
                                if (progress === result.length ) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                        }
                    }else{
                        res.json([]);
                        conn.release();
                    }

                })
            }

        })
    }
});

//获取账单明细
app.get('/getDetails',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('SELECT p.* from paylog p WHERE p.managerId=?  order by payTime desc', [managerId], (err, paylogs)=> {
                    var progress = 0;
                    for (let paylog of paylogs) {
                        conn.query('SELECT m.inviteCode,m.name,m.power_id,m.rebate,a.Uuid as muuid FROM manager m,account a WHERE m.id=? and a.managerId = m.id', [paylog.managerId], (err, mana)=> {
                            paylog['inviteCode'] = mana[0].inviteCode;
                            paylog['name'] = mana[0].name;
                            paylog['power_id'] = mana[0].power_id;
                            paylog['rebate'] = mana[0].rebate;
                            paylog['muuid'] = mana[0].muuid;
                            progress++;
                            if (progress === paylogs.length) {
                                //console.log(result);
                                res.json(paylogs);
                                conn.release();
                            }
                        })
                    }
                })
            }

        });
    }
});

//获取充值总额select IFNULL(sum(a.money),0) from paylog a,manager b where a.managerId = b.id and a.payType = 0
app.get('/getTotalMoney',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var levelStr='';
        var n=100000000;
        var levelStr0=n+parseInt(managerId);
        var levelStr1=levelStr0+'$%';
        levelStr=levelStr1.slice(1,levelStr1.length-1);
        var plevelStr='';
        plevelStr=user.levelStr;
        if(plevelStr){
            levelStr=plevelStr+levelStr;
        }
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('select IFNULL(sum(a.money),0) as totalmoney from paylog a,manager b where a.managerId = b.id and a.payType = 0 and (b.levelStr like ? or b.id =?) and a.status != 2 ', [levelStr,managerId], (err, totalMoney)=> {
                    console.log('totalMoney:'+totalMoney[0]);
                    res.json(totalMoney[0]);
                    conn.release();
                })
            }

        });
    }
});

//获取账单明细
app.get('/getPaylogs',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var levelStr='';
        var n=100000000;
        var levelStr0=n+parseInt(managerId);
        var levelStr1=levelStr0+'$%';
        levelStr=levelStr1.slice(1,levelStr1.length-1);
        var plevelStr='';
        plevelStr=user.levelStr;
        if(plevelStr){
            levelStr=plevelStr+levelStr;
        }
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('select a.*,c.nickName from paylog a,manager b,account c where c.Uuid=a.uuid and a.managerId = b.id and a.payType = 0 and (b.levelStr like ? or b.id =?) and a.status != 2 ', [levelStr,managerId], (err, paylogs)=> {
                    console.log(paylogs);
                    if(paylogs.length>0){
                        var progress=0;
                        for(let paylog of paylogs){
                            conn.query('select inviteCode,name,rebate,power_id,manager_up_id from manager where id=?',[paylog.managerId],(err,parentM)=>{
                                console.log('parentM');
                                console.log(parentM);
                                if(parentM[0].manager_up_id){
                                    //conn.query('')
                                }
                            })
                        }
                    }else{
                        res.json([]);
                        conn.release();
                    }
                    res.json(paylogs);
                    conn.release();
                })
            }

        });
    }
});

//修改密码/resetPassword
app.post('/resetPassword',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            console.log(obj);
            var newPwd = obj.newPwd;
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('UPDATE manager SET password=? WHERE id=?', [newPwd, managerId], (err, result)=> {
                        console.log(result);
                        //var oid = result.insertId;
                        if(result.changedRows>0){
                            res.json({"status": 1});
                        }else{
                            res.json({"status": 0});
                        }
                        conn.release();
                    });

                }
            })
        });
    }
});


//验证邀请码
app.get('/validInviteCode',(req,res)=>{
    if(req.session.user){
        var managerId=req.query.managerId;
        var inviteCode = req.query.inviteCode;

        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM manager  WHERE inviteCode=? and id!=?',[inviteCode,managerId],(err,result)=>{
                    console.log(result);
                    res.json(result);
                })
            }
            conn.release();
        })
    }
});

//新增代理验证邀请码addValidInviteCode
app.get('/addValidInviteCode',(req,res)=>{
    if(req.session.user){
        var inviteCode = req.query.inviteCode;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM manager  WHERE inviteCode=?',[inviteCode],(err,result)=>{
                    console.log(result);
                    res.json(result);
                })
            }
            conn.release();
        })
    }
});
//验证游戏ID
app.get('/validUuid',(req,res)=>{
    if(req.session.user){
        var managerId=req.query.mid;
        var uuid = req.query.uuid;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid],(err,result)=>{
                    if(result.length>0){
                        if(result[0].managerId>0){
                            if(result[0].managerId==managerId){
                                res.json({"status":1});
                            }else{
                                res.json({"status":0});
                            }
                        }else{
                            res.json({"status":1});
                        }
                    }else{
                        res.json({"status":0});
                    }
                })
            }
            conn.release();
        })
    }
});
//新增代理验证游戏ID addValidUuid
app.get('/addValidUuid',(req,res)=>{
    if(req.session.user){
        var managerId=req.query.mid;
        var uuid = req.query.uuid;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid],(err,result)=>{
                    if(result.length>0){
                        if(result[0].managerId>0){
                            res.json({"validuuid":0});
                        }else{
                            result[0]['validuuid']=1;
                            res.json(result[0]);
                        }
                    }else{
                        res.json({"validuuid":0});
                    }
                })
            }
            conn.release();
        })
    }
});
//玩家充值验证游戏ID vipChargeValidUuid
app.get('/vipChargeValidUuid',(req,res)=>{
    if(req.session.user){
        var user=req.session.user;
        var managerId=user.id;
        var uuid = req.query.uuid;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM account  WHERE Uuid=? AND manager_up_id=? AND status!=2',[uuid,managerId],(err,result)=>{
                    if(result.length>0){
                        res.json({"validuuid":1});
                    }else{
                        res.json({"validuuid":0});
                    }
                })
            }
            conn.release();
        })
    }
});

//修改代理信息
app.post('/updateManagerInfo',(req,res)=>{
    if(req.session.user) {
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            console.log(obj);
            var managerId=obj.mid;
            var inviteCode = obj.inviteCode;
            var powerId = obj.powerId;
            var status = obj.status;
            var telephone=obj.telephone;
            var rebate=obj.rebate;
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('UPDATE  manager SET inviteCode=?,power_id=?,status=?,telephone=?,rebate=?  WHERE id=?', [inviteCode,powerId,status,telephone,rebate,managerId], (err, result)=> {
                        console.log(result);
                        if(result.changedRows>0){
                            res.json({"status": 1});
                        }else{
                            res.json({"status": 0});
                        }
                        conn.release();
                    });

                }
            })
        });
    }
});

//代理充值
app.post('/updateAccount',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var powerId = user.power_id;
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            console.log(obj);
            var uuid=obj.uuid;
            var roomCardNum = obj.roomCardNum;
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    if(powerId==1){
                        conn.query('UPDATE  account SET roomCard=roomCard+?  WHERE Uuid=?', [roomCardNum,uuid], (err, result)=> {
                            console.log(result);
                            if(result.changedRows>0){
                                res.json({"status": 1});
                            }else{
                                res.json({"status": 0});
                            }
                            conn.release();
                        });
                    }else{
                        conn.query('SELECT * FROM account WHERE managerId=?', [managerId], (err, result)=> {
                            console.log(result);
                            if(result[0].roomCard<roomCardNum){
                                res.json({"status": 0});
                            }else{
                                conn.query('UPDATE account SET roomCard =roomCard-? WHERE managerId=?',[roomCardNum,managerId],(err,resu)=>{
                                    console.log(resu);
                                    if(resu.changedRows>0){
                                        conn.query('UPDATE account SET roomCard =roomCard+? WHERE Uuid=?',[roomCardNum,uuid],(err,resul)=>{
                                            console.log(resul);
                                            if(resul.changedRows>0){
                                                res.json({"status": 1});
                                            }else{
                                                res.json({"status": 0});
                                            }
                                        })
                                    }else{
                                        res.json({"status": 0});
                                    }

                                });

                            }
                            conn.release();
                        });
                    }


                }
            })
        });


    }
});

//玩家充值
app.post('/vipCharge',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var powerId = user.power_id;
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            console.log(obj);
            var uuid=obj.uuid;
            var roomCardNum = obj.roomCardNum||0;
            var redCardNum = obj.redCardNum||0;
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    if(powerId==1){
                        conn.query('UPDATE  account SET roomCard=roomCard+?,redCard=redCard+?  WHERE Uuid=?', [roomCardNum,redCardNum,uuid], (err, result)=> {
                            console.log(result);
                            if(result.changedRows>0){
                                res.json({"status": 1});
                            }else{
                                res.json({"status": 0});
                            }
                            conn.release();
                        });
                    }else{
                        conn.query('SELECT * FROM account WHERE managerId=?', [managerId], (err, result)=> {
                            console.log(result);
                            if(result[0].roomCard<roomCardNum||result[0].redCard<redCardNum){
                                res.json({"status": 0});
                            }else{
                                conn.query('UPDATE account SET roomCard =roomCard-?,redCard=redCard-? WHERE managerId=?',[roomCardNum,redCardNum,managerId],(err,resu)=>{
                                    console.log(resu);
                                    if(resu.changedRows>0){
                                        conn.query('UPDATE account SET roomCard =roomCard+?,redCard=redCard+? WHERE Uuid=?',[roomCardNum,redCardNum,uuid],(err,resul)=>{
                                            console.log(resul);
                                            if(resul.changedRows>0){
                                                res.json({"status": 1});
                                            }else{
                                                res.json({"status": 0});
                                            }
                                        })
                                    }else{
                                        res.json({"status": 0});
                                    }

                                });

                            }
                            conn.release();
                        });
                    }


                }
            })
        });


    }
});

//验证上级代理邀请码
app.get('/validParentInviteCode',(req,res)=>{
    if(req.session.user){
        var pinviteCode = req.query.parentInviteCode;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM manager  WHERE inviteCode=? ',[pinviteCode],(err,result)=>{
                    res.json(result);
                })
            }
            conn.release();
        })
    }
});

//新增代理信息 e10adc3949ba59abbe56e057f20f883e
app.post('/insertManager',(req,res)=>{
    if(req.session.user) {
        var user=req.session.user;
        var powerId=user.power_id;
        var pmId=user.id;
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            console.log(obj);
            var uname=obj.uname;
            var uuid=obj.uuid;
            var inviteCode = obj.inviteCode;
            var pinviteCode=obj.parentInviteCode;
            var tel=obj.telephone;
            var weixin = obj.weixin;
            var qq = obj.qq;
            var powerId = obj.powerId;
            var pmid = obj.pmid;
            var pwd='e10adc3949ba59abbe56e057f20f883e';
            var redCard=obj.redCard;
            var levelStr0=100000000;
            var levelStr1=parseInt(levelStr0)+parseInt(pmid);
            var levelStr2=levelStr1+'$';
            var levelStr = levelStr2.slice(1,levelStr2.length-1);
            var rebate=0;
            if(obj.rebate){
                rebate=obj.rebate;
            }else{
                if(powerId==5){
                    rebate=0.7;
                }else if(powerId==4){
                    rebate=0.6;
                }else if(powerId==3){
                    rebate=0.5;
                }else if(powerId==2){
                    rebate=0.4;
                }
            }

            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('INSERT INTO manager VALUES(null,?,?,?,?,0,0,?,0,?,?,?,1,?,1,?,?,now(),?)', [powerId,uname,tel,pwd,pmid,inviteCode,weixin,qq,rebate,levelStr,uuid,redCard], (err, result)=> {
                        console.log(result);
                        if(result.affectedRows>0){
                            conn.query('UPDATE account SET manager_up_id=?,managerId=? WHERE Uuid=?',[result.insertId,result.insertId,uuid],(err,resultaccount)=>{
                                console.log("resultaccount:"+resultaccount);
                                res.json({"status":1});
                            })
                        }else{
                            res.json({"status":0});
                        }
                        conn.release();

                    });

                }
            })
        });
    }
});

//根据玩家ID查询玩家信息 searchVipByUuid
app.get('/searchVipByUuid',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var starttime=req.query.starttime;
        var endtime=req.query.endtime;
        var now=new Date();
        now.setDate(now.getDate()+1);
        var overArr=now.toLocaleDateString().split('/');
        for(var i=0;i<overArr.length;i++){
            if(overArr[i]<10){
                overArr[i]=0+overArr[i];
            }
        }
        var overTime=overArr.join('-');
        console.log(overTime);
        if(!starttime){
            starttime='1970-01-01';
        }
        if(!endtime){
            endtime=overTime;
        }
        var uuid=req.query.uuid;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id and a.Uuid=? order by a.createTime desc', [managerId,uuid], (err, result)=> {
                    console.log("+++"+result);
                    if(result.length>0){
                        var progress=0;
                        for(let account of result){
                            conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime between ? and ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                console.log(sum);
                                if (sum[0].m) {
                                    account['sumMoney'] = sum[0].m;
                                } else {
                                    account['sumMoney'] = 0;
                                }
                                progress++;
                                if (progress === result.length ) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                        }
                    }else{
                        res.json([]);
                        conn.release();
                    }

                })
            }

        })
    }
});

// searchVipByTime
app.get('/searchVipByTime',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var starttime=req.query.starttime;
        var endtime=req.query.endtime;
        var now=new Date();
        now.setDate(now.getDate()+1);
        var overArr=now.toLocaleDateString().split('/');
        for(var i=0;i<overArr.length;i++){
            if(overArr[i]<10){
                overArr[i]=0+overArr[i];
            }
        }
        var overTime=overArr.join('-');
        console.log(overTime);
        if(!starttime){
            starttime='1970-01-01';
        }
        if(!endtime){
            endtime=overTime;
        }
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id  order by a.createTime desc', [managerId], (err, result)=> {
                    console.log("+++"+result);
                    if(result.length>0){
                        var progress=0;
                        for(let account of result){
                            conn.query('select sum(p.money) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime between ? and ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                console.log(sum);
                                if (sum[0].m) {
                                    account['sumMoney'] = sum[0].m;
                                } else {
                                    account['sumMoney'] = 0;
                                }
                                progress++;
                                if (progress === result.length ) {
                                    //console.log(result);
                                    res.json(result);
                                    conn.release();
                                }
                            });
                        }
                    }else{
                        res.json([]);
                        conn.release();
                    }

                })
            }

        })
    }
});
