/**
 * Created by Administrator on 2017-12-29.
 */
const pool = require('./pool');
const qs=require('querystring');

module.exports = {
    login:(req,res)=>{
        var uname = req.query.uname;
        var pwd = req.query.pwd;
        var code = req.query.code;

        function login(){
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT * FROM manager WHERE uuid=? and password = ? and status = 0 and uuid>0',[uname,pwd],(err,result)=>{

                        // console.log('loginlogin');
                        // console.log(result);
                        if(result.length>0){
                            conn.query('UPDATE manager SET lastLoginTime=now() WHERE uuid=?',[uname],(err,result)=>{
                                if(err){
                                    console.log(err);
                                }else{
                                    // console.log(result);
                                }
                            });
                            result[0]['msg']='登录成功！';
                            result[0]['logStatus']=1;
                            req.session.user=result[0];
                            res.json(result[0]);
                        }else{
                            res.json({"msg":'用户名或密码不正确！',"logStatus":0})
                        }
                    })
                }
                conn.release();
            })
        }
        if(req.session.code==code){
            if(req.session.user){
                //var user=req.session.user;
                //if(uname==user.inviteCode&&pwd==user.password){
                //    res.json(user);
                //}else{
                //    login();
                //}
                login();
            }else{
                login();
            }
        }else{
            res.json({"msg":"验证码不正确！请重新输入","logStatus":0})
        }


    },
    validInviteCode:(req,res)=>{
        if(req.session.user){
            var managerId=req.query.managerId;
            var inviteCode = req.query.inviteCode;

            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT * FROM manager  WHERE inviteCode=? and id!=?',[inviteCode,managerId],(err,result)=>{
                        // console.log(result);
                        res.json(result);
                    })
                }
                conn.release();
            })
        }
    },
    getlevelStr:(req,res)=>{
            var managerId=req.query.managerId;
            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    conn.query('select levelStr from manager where id=?', [managerId], (err, result)=> {
                        // console.log(result);
                        res.json(result);
                    });

                }
                conn.release();
            })
    },
    getAgentInfo:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.id=? and m.id = a.managerId',[managerId],(err,result)=>{
                        //console.log(result);
                        result[0].lastLoginTime=user.lastLoginTime;
                        res.json(result[0]);
                    })
                }
                conn.release();
            })
        }
    },
    resetPassword:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var managerId = user.id;
            req.on("data", (buff)=> {
                var obj = qs.parse(buff.toString());
                // console.log(obj);
                var newPwd = obj.newPwd;
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        conn.query('UPDATE manager SET password=? WHERE id=?', [newPwd, managerId], (err, result)=> {
                            // console.log(result);
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
    },
    addValidInviteCode:(req,res)=>{
        if(req.session.user){
            var inviteCode = req.query.inviteCode;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT * FROM manager  WHERE inviteCode=?',[inviteCode],(err,result)=>{
                        // console.log(result);
                        res.json(result);
                    })
                }
                conn.release();
            })
        }
    },
    validManagerId:(req,res)=>{
        if(req.session.user){
            var managerId = req.query.managerId;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT * FROM manager  WHERE id=?',[managerId],(err,result)=>{
                        // console.log(result);
                        if(result.length>0){
                            result[0]['validmid']=1;
                            res.json(result);
                        }else{
                            res.json([{"validmid":0}]);
                        }
                    })
                }
                conn.release();
            })
        }
    },
    reupCode:(req,res)=>{
        if(req.session.user){
            var managerId = req.query.managerId;
            var pmid = req.query.pmid;
            var levelStr = req.query.levelStr;
            var slevelStr='';
            var n=100000000;
            var levelStr0=n+parseInt(managerId);
            var levelStr1=levelStr0+'$';
            slevelStr=levelStr1.slice(1);
            if(levelStr){
                slevelStr=levelStr+slevelStr;
            }
            if(req.session.user.power_id==1){
                pool.getConnection((err,conn)=>{
                    if(err){
                        console.log(err);
                    }else{
                        conn.query('update manager set manager_up_id=?,levelStr=? where id=?',[pmid,levelStr,managerId],(err,result)=>{
                            // console.log(result);
                            if(result.changedRows>0){
                                conn.query('update manager set levelStr=? where manager_up_id=?',[slevelStr,managerId],(err,result0)=>{
                                    if(err){
                                        console.log(err);
                                    }
                                });
                                res.json({"status":1});
                            }else{
                                res.json({"status":0});
                            }
                        })
                    }
                    conn.release();
                })
            }else{
                res.json([{"status":0}]);
            }

        }
    },
    addValidUuid:(req,res)=>{
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
    },
    validUuid:(req,res)=>{
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
    },
    updateManagerInfo:(req,res)=>{
        if(req.session.user) {
            req.on("data", (buff)=> {
                var obj = qs.parse(buff.toString());
                // console.log(obj);
                var managerId=obj.mid;
                var inviteCode = obj.inviteCode;
                var powerId = obj.powerId;
                var status = obj.status;
                var telephone=obj.telephone;
                var rebate=obj.rebate;
                var uuid=obj.uuid;
                var weixin=obj.weixin;
                var rootManager=obj.rootManager;
                var uname=obj.uname;
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        conn.query('UPDATE  manager SET name=?,inviteCode=?,power_id=?,status=?,telephone=?,rebate=?,uuid=?,weixin=?,rootManager=?  WHERE id=?', [uname,inviteCode,powerId,status,telephone,rebate,uuid,weixin,rootManager,managerId], (err, result)=> {
                            // console.log(result);
                            if(result.changedRows>0){
                                conn.query('UPDATE account SET managerId=?,manager_up_id=? WHERE Uuid=?',[managerId,managerId,uuid],(err,result1)=>{
                                    if(err){
                                        console.log(err);
                                    }
                                })
                                conn.query('UPDATE account SET managerId=0 WHERE managerId=? and uuid!=?',[managerId,uuid],(err,result2)=>{
                                    if(err){
                                        console.log(err);
                                    }
                                })
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
    },
    updateAccount:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var managerId = user.id;
            var powerId = user.power_id;
            req.on("data", (buff)=> {
                var obj = qs.parse(buff.toString());
                // console.log(obj);
                var uuid=obj.uuid;
                var roomCardNum = obj.roomCardNum;
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        if(powerId==1){
                            conn.query('UPDATE  account SET roomCard=roomCard+?  WHERE Uuid=?', [roomCardNum,uuid], (err, result)=> {
                                // console.log(result);
                                if(result.changedRows>0){
                                    conn.query('insert into roomcardlog values(null,?,?,?,now())',[managerId,uuid,roomCardNum],(err,result)=>{
                                        if(err){
                                            console.log(err);
                                        }
                                    })
                                    res.json({"status": 1});
                                }else{
                                    res.json({"status": 0});
                                }
                                conn.release();
                            });
                        }else{
                            conn.query('SELECT * FROM account WHERE managerId=?', [managerId], (err, result)=> {
                                // console.log(result);
                                if(result[0].roomCard<roomCardNum){
                                    res.json({"status": 0});
                                }else{
                                    conn.query('UPDATE account SET roomCard =roomCard-? WHERE managerId=?',[roomCardNum,managerId],(err,resu)=>{
                                        console.log(resu);
                                        if(resu.changedRows>0){
                                            conn.query('UPDATE account SET roomCard =roomCard+? WHERE Uuid=?',[roomCardNum,uuid],(err,resul)=>{
                                                // console.log(resul);
                                                if(resul.changedRows>0){
                                                    conn.query('insert into roomcardlog values(null,?,?,?,now())',[managerId,uuid,roomCardNum],(err,result)=>{
                                                        if(err){
                                                            console.log(err);
                                                        }
                                                    })
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
    },
    validParentInviteCode:(req,res)=>{
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
    },
    insertManager:(req,res)=>{
        if(req.session.user) {
            var user=req.session.user;
            var userPowerId=user.power_id;
            var pmid=user.id;
            req.on("data", (buff)=> {
                var obj = qs.parse(buff.toString());
                // console.log(obj);
                var uname=obj.uname;
                var uuid=obj.uuid;
                var inviteCode = obj.inviteCode;
                var pinviteCode=obj.parentInviteCode;
                var tel=obj.telephone;
                var weixin = obj.weixin;
                var qq = obj.qq;
                var rootManager = obj.rootManager;
                var powerId = obj.powerId;
                pmid = obj.pmid;
                var pwd='';
                if(obj.pwdmd5){
                    pwd =obj.pwdmd5;
                }else{
                    pwd='e10adc3949ba59abbe56e057f20f883e';
                }
                var redCard=obj.redCard;
                var plevelStr=obj.plevelStr;
                var levelStr='';
                if(pmid>1){
                    var levelStr0=100000000;
                    var levelStr1=parseInt(levelStr0)+parseInt(pmid);
                    var levelStr2=levelStr1+'$';
                    levelStr = levelStr2.slice(1);
                    if(plevelStr){
                        levelStr=plevelStr+levelStr;
                    }
                }
                var rebate=0;
                if(obj.rebate){
                    rebate=obj.rebate;
                }else{
                    if(powerId==5){
                        rebate=0.6;
                    }else if(powerId==4){
                        rebate=0.5;
                    }else if(powerId==3){
                        rebate=0.4;
                    }else if(powerId==2){
                        rebate=0.35;
                    }
                }
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        conn.query('INSERT INTO manager VALUES(null,?,?,?,?,0,0,?,0,?,?,?,?,?,1,?,?,now(),?,null)', [powerId,uname,tel,pwd,pmid,inviteCode,weixin,qq,rootManager,rebate,levelStr,uuid,redCard], (err, result)=> {
                            // console.log(result);
                            if(result.affectedRows>0){
                                conn.query('UPDATE account SET manager_up_id=?,managerId=? WHERE Uuid=?',[result.insertId,result.insertId,uuid],(err,resultaccount)=>{
                                    // console.log("resultaccount:"+resultaccount);
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
    },
    deleteManager:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=req.query.managerId;
            var powerId=user.power_id;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId==1){
                        conn.query('delete from manager where id=?',[managerId],(err,result)=>{
                            console.log(result);
                            if(result.affectedRows>0){
                                conn.query('update account set manager_up_id=?,managerId=? where managerId=? or manager_up_id=?',[null,null,managerId,managerId],(err,result0)=>{
                                    console.log(result0);
                                })
                            }
                            res.json(result.affectedRows);
                        })
                    }else{
                        res.json(0);
                    }
                }
                conn.release();
            })
        }
    },
    getVipCount:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var levelStr='';
            var n=100000000;
            var levelStr0=n+parseInt(managerId);
            var levelStr1=levelStr0+'$%';
            levelStr=levelStr1.slice(1);
            var plevelStr='';
            plevelStr=user.levelStr;
            if(plevelStr){
                levelStr=plevelStr+levelStr;
            }
            var powerId=user.power_id;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId==1){
                        conn.query('select COUNT(a.id) as vipCount from account a ',(err,result)=>{
                            // console.log(9999999999);
                            //console.log(result);
                            res.json(result[0]);
                        })
                    }else{
                        conn.query('select COUNT(a.id) as vipCount from account a ,manager b where a.manager_up_id = b.id and (a.manager_up_id = ? or  b.levelStr like ?)',[managerId,levelStr],(err,result)=>{
                            //console.log(9999999999);
                            //console.log(result);
                            res.json(result[0]);
                        })
                    }
                }
                conn.release();
            })
        }
    },
    getAgentCount:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var levelStr='';
            var n=100000000;
            var levelStr0=n+parseInt(managerId);
            var levelStr1=levelStr0+'$%';
            levelStr=levelStr1.slice(1);
            var plevelStr='';
            plevelStr=user.levelStr;
            if(plevelStr){
                levelStr=plevelStr+levelStr;
            }
            var powerId=user.power_id;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId==1){
                        conn.query('select COUNT(m.id) as agentCount from manager m WHERE m.id>1',(err,result)=>{
                            //console.log(9999999999);
                            //console.log(result);
                            res.json(result[0]);
                        })
                    }else{
                        conn.query('select COUNT(m.id) as agentCount from manager m WHERE m.manager_up_id=?',[managerId],(err,result)=>{
                            //console.log(9999999999);
                            //console.log(result);
                            res.json(result[0]);
                        })
                    }
                }
                conn.release();
            })
        }
    },
    getmineone:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var starttime=req.query.starttime;
            var endtime=req.query.endtime;
            var rebate=parseFloat(user.rebate);
            var now=new Date();
            now.setDate(now.getDate()+1);
            var overArr=now.toLocaleDateString().split('/');
            for(var i=0;i<overArr.length;i++){
                if(overArr[i]<10){
                    overArr[i]=0+overArr[i];
                }
            }
            var overTime=overArr.join('-');
            // console.log(overTime);
            if(!starttime){
                starttime='1970-01-01';
            }
            if(!endtime){
                endtime=overTime;
            }
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('select IFNULL(sum(money),0)as mineone from paylog where managerId =? and payTime > ? and payTime < ? and payType = 0 and gameId=11  and payTime > (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and (payType = 1 or payType = 2) and status = 1)',[managerId,starttime,endtime,managerId],(err,result)=>{
                        // console.log('mineone=====');
                        // console.log(result);
                        req.session.mineone=(result[0].mineone)*rebate;
                        res.json({"mineone":(result[0].mineone)*rebate});
                    })
                }
                conn.release();
            })
        }
    },
    getminetwo:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
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
            // console.log(overTime);
            if(!starttime){
                starttime='1970-01-01';
            }
            if(!endtime){
                endtime=overTime;
            }
            var levelStr='';
            var n=100000000;
            var levelStr0=n+parseInt(managerId);
            var levelStr1=levelStr0+'$%';
            levelStr=levelStr1.slice(1);
            var plevelStr='';
            plevelStr=user.levelStr;
            if(plevelStr){
                levelStr=plevelStr+levelStr;
            }
            var length=levelStr.length;
            var rebate=parseFloat(user.rebate);
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('select IFNULL(sum(n.money*(?-(o.rebate+0.0))),0.0) as minetwo from (select sum(m.money) as money,m.top1mid from (select sum(a.money) as money,b.id,(case when (substring(b.levelStr,?,8)+0)=0 then b.id else (substring(b.levelStr,?,8)+0) end) as top1mid from paylog a,manager b where a.managerId = b.id  and a.payType = 0 and a.gameId=11 and a.payTime > (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and payType = 1 and status = 1) and b.levelStr like ? group by id,top1mid) m group by m.top1mid) n,manager o where n.top1mid = o.id',[rebate,length,length,managerId,levelStr],(err,result)=>{
                        // console.log('minetwo=====');
                        // console.log(result);
                        req.session.minetwo=result[0].minetwo;
                        res.json(result[0]);
                    })
                }
                conn.release();
            })
        }
    },
    getMyAgents:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var managerId = user.id;
            if(req.query.managerId){
                managerId=req.query.managerId
            }
            var powerId=user.power_id;
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
            // console.log(overTime);
            if(!starttime){
                starttime='1970-01-01';
            }
            if(!endtime){
                endtime=overTime;
            }
            var inputPowerId=req.query.powerId;
            var limitstart=(req.query.page-1)*10;
            var uname=req.query.uname;
            var gameId=req.query.gameId;
            var inviteCode=req.query.invitecode;
            // console.log(starttime,endtime,uname,inviteCode);
            var resultJson={managers:[],totalNum:0,totalMoney:0};
            if(powerId==1){
                if(req.query.managerId){
                    if(!uname&&!inviteCode){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ?  and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o  ', [managerId,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ?  and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o  ', [managerId,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=? and power_id=?',[managerId,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o  ', [managerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o  ', [managerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?',[managerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }else if(uname&&inviteCode){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and name=? and inviteCode=? and power_id=?',[managerId,uname,inviteCode,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and name=? and inviteCode=?',[managerId,uname,inviteCode],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }

                            }
                        })
                    }else if(uname&&!inviteCode){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o ', [managerId,uname,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o ', [managerId,uname,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and name=? and power_id=?',[managerId,uname,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o ', [managerId,uname,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o ', [managerId,uname,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and name=?',[managerId,uname],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }else if(inviteCode&&!uname){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and inviteCode=? and power_id=?',[managerId,inviteCode,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and inviteCode=?',[managerId,inviteCode],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }
                }else{
                    if(!uname&&!inviteCode){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where id>3 and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where id>3 and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where id>3 and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where id>3 and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where id>3 and power_id=?',[inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=1 and uuid>0) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id<4 and id>3 and uuid>0) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where m.manager_up_id<4 and id>3 and uuid>0',(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }else if(uname&&inviteCode){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id group by q.id)o', [uname,inviteCode,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id group by q.id)o', [uname,inviteCode,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where name=? and inviteCode=? and power_id=?',[uname,inviteCode,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and  p.payTime>? and p.payTime< ? and p.managerId=q.id group by q.id)o', [uname,inviteCode,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id group by q.id)o', [uname,inviteCode,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where name=? and inviteCode=?',[uname,inviteCode],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }else if(uname&&!inviteCode){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where name=? and power_id=?',[uname,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id group by r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where name=? ',[uname],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }else if(inviteCode&&!uname){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(inputPowerId){
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,inputPowerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o',[inviteCode,inputPowerId,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o',[inviteCode,inputPowerId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }

                                    conn.query('select count(m.id) as totalNum from manager m where inviteCode=? and power_id=?',[inviteCode,inputPowerId],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }else{
                                    if(gameId){
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,gameId,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o',[inviteCode,gameId,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }else{
                                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                            //console.log(result);
                                            resultJson.managers=result;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                        conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0   and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o',[inviteCode,starttime,endtime], (err, result)=> {
                                            //console.log(result);
                                            resultJson.totalMoney=result[0].sumMoney;
                                            progress++;
                                            if(progress==3){
                                                res.json(resultJson);
                                                conn.release();
                                            }
                                        });
                                    }
                                    conn.query('select count(m.id) as totalNum from manager m where inviteCode=?',[inviteCode],(err,result)=>{
                                        resultJson.totalNum=result[0].totalNum;
                                        progress++;
                                        if(progress==3){
                                            res.json(resultJson);
                                            conn.release();
                                        }
                                    })
                                }
                            }
                        })
                    }
                }

            }else{
                if(!uname&&!inviteCode){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            if(gameId){
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,gameId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }
                            conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?',[managerId],(err,result)=>{
                                resultJson.totalNum=result[0].totalNum;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
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
                            var progress=0;
                            if(gameId){
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,gameId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('SELECT IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,gameId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('SELECT IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }
                            conn.query('select count(m.id) as totalNum from manager m where manager_up_id=? and name=? and inviteCode=?',[managerId,uname,inviteCode],(err,result)=>{
                                resultJson.totalNum=result[0].totalNum;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
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
                            var progress=0;
                            if(gameId){
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,managerId,gameId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('SELECT IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=?  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,managerId,gameId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,managerId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('SELECT IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,managerId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }
                            conn.query('select count(m.id) as totalNum from manager m where name=? and manager_up_id=?',[uname,managerId],(err,result)=>{
                                resultJson.totalNum=result[0].totalNum;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
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
                            var progress=0;
                            if(gameId){
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,gameId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('SELECT IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0   and p.gameId=? and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,gameId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('SELECT IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                            }
                            conn.query('select count(m.id) as totalNum from manager m where manager_up_id=? and inviteCode=?',[managerId,inviteCode],(err,result)=>{
                                resultJson.totalNum=result[0].totalNum;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                        }
                    })
                }
            }


        }
    },
    getChildAgents:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var managerId = req.query.managerId;
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
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and uuid>0) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ?  and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 and a.Uuid=s.uuid ORDER BY totalMoney desc,userCounts desc', [managerId,starttime,endtime],(err,result)=>{
                        res.json(result);
                    })
                }
                conn.release();
            })



        }
    },
    getRemain:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('select money from paylog where payType = 9 and managerId = ? and payTime = (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and (payType = 9) and status = 1) ',[managerId,managerId],(err,result)=>{
                        if(err){
                            console.log(err);
                        }else{
                            // console.log('remainremain');
                            // console.log(result);
                            if(result.length>0){
                                req.session.remain=result[0].money;
                            }else{
                                req.session.remain=0;
                            }
                            // console.log('req.session.remain'+req.session.remain);
                            //req.session.remain=result[0].money||0;
                            res.json(result);
                        }
                    })
                }
                conn.release();
            })
        }
    },
    getManagers:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var powerId=user.power_id;
            var inputManagerId=req.query.managerId;
            var uname =req.query.uname;
            var inviteCode=req.query.inviteCode;
            var inputPowerId=req.query.powerId;
            var uuid=req.query.uuid;
            if(inputManagerId){
                managerId=req.query.managerId;
            }
            var levelStr='';
            var n=100000000;
            var levelStr0=n+parseInt(managerId);
            var levelStr1=levelStr0+'$%';
            levelStr=levelStr1.slice(1);
            var plevelStr='';
            plevelStr=user.levelStr;
            if(plevelStr){
                levelStr=plevelStr+levelStr;
            }
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
            // console.log(overTime);
            if(!starttime){
                starttime='1970-01-01';
            }
            if(!endtime){
                endtime=overTime;
            }
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId>1||inputManagerId){
                        if(uname){
                            if(inviteCode){
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.inviteCode=? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,inviteCode,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.inviteCode=? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,inviteCode,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.inviteCode=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,inviteCode,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.inviteCode=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,inviteCode,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }else{
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.name=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uname,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }
                        }else{
                            if(inviteCode){
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.inviteCode=? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,inviteCode,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.inviteCode=? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,inviteCode,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })

                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.inviteCode=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 12 or a.gameId = 11) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,inviteCode,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.inviteCode=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,inviteCode,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }else{
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.levelStr like ?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[levelStr,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }

                        }
                    }else{
                        if(uname){
                            if(inviteCode){
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.inviteCode=? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,inviteCode,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.inviteCode=? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId =12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,inviteCode,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.inviteCode=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,inviteCode,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.inviteCode=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,inviteCode,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }else{
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.name=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uname,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }
                        }else{
                            if(inviteCode){
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.inviteCode=? and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[inviteCode,uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.inviteCode=? and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[inviteCode,uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.inviteCode=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[inviteCode,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.inviteCode=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[inviteCode,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }else{
                                if(uuid){
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.uuid=? and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uuid,inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.uuid=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId =12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[uuid,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }else{
                                    if(inputPowerId){
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3 and b.power_id=?) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[inputPowerId,starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }else{
                                        conn.query("select m.*,IFNULL(sum(n.money),0) as totalMoney from  (select b.*,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$%') as totalLevelStr,IFNULL(count(a.id),0) as userCounts  from account a right join manager b on a.manager_up_id = b.id group by b.id having b.id>3) m left join(select b.id,concat(IFNULL(b.levelStr,''),LPAD(b.id, 8, 0),'$') as levelStr,IFNULL(sum(a.money),0) as money from manager b left join paylog a on a.managerId = b.id and a.payTime >? and a.payTime <? and  b.pid=1  and (a.gameId = 11 or a.gameId = 12) and payType = 0 group by b.id having b.id>2 ) n on n.levelStr like m.totalLevelStr group by m.id ORDER BY totalMoney desc,totalCards desc ",[starttime,endtime],(err,result)=>{
                                            //console.log(result);
                                            res.json(result);
                                        })
                                    }
                                }
                            }
                        }
                    }
                }
                conn.release();
            })
        }
    },
    getAgentNotice:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('select * from noticetable where type=3 order by createTime desc limit 0,1',(err,result)=>{
                        if(err){
                            console.log(err);
                        }else{
                            res.json(result[0]);
                        }
                    })
                }
                conn.release();
            })
        }
    }
}
