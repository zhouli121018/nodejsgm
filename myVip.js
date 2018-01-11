/**
 * Created by Administrator on 2017-12-29.
 */
const pool = require('./pool');
const qs=require('querystring');

module.exports = {
    getAccount:(req,res)=>{
        var user = req.session.user;
        var managerId = user.id;
        var powerId=user.power_id;
        var inputManagerId = req.query.managerId;
        var uuid=req.query.uuid;
        var limitstart=(req.query.page-1)*10;
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
        var resultJson={accounts:[],totalNum:0};
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                if(powerId==1||powerId==5||powerId==4){
                    if(inputManagerId){
                        if(uuid){
                            var progress=0;
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE a.manager_up_id=? and a.Uuid=?)n LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime<? and p.uuid=n.Uuid group by n.id ',[inputManagerId,uuid,starttime,endtime],(err,result)=>{
                                resultJson.accounts=result;
                                progress++;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                            conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE a.manager_up_id=? and a.uuid=?',[inputManagerId,uuid],(err,result)=>{
                                progress++;
                                resultJson.totalNum=result[0].totalNum;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                        }else{
                            var progress=0;
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.*,m.name,m.power_id FROM account a left join manager m on  a.manager_up_id=m.id WHERE a.manager_up_id=?)n LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime<? and p.uuid=n.Uuid group by n.id order by totalMoney desc,createTime desc limit ?,10',[inputManagerId,starttime,endtime,limitstart],(err,result)=>{
                                resultJson.accounts=result;
                                progress++;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE a.manager_up_id=?',[inputManagerId],(err,result)=>{
                                progress++;
                                resultJson.totalNum=result[0].totalNum;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                        }

                    }else{
                        if(uuid){
                            var progress=0;
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE  a.Uuid=?)n LEFT JOIN paylog p on p.payTime>? and p.payType=0  and p.payTime<? and p.uuid=n.Uuid group by n.id ',[uuid,starttime,endtime],(err,result)=>{
                                resultJson.accounts=result;
                                progress++;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                            conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE  a.uuid=?',[uuid],(err,result)=>{
                                progress++;
                                resultJson.totalNum=result[0].totalNum;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                        }else{
                            var progress=0;
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from (SELECT a.*,m.name,m.power_id FROM account a LEFT JOIN manager m on m.id=a.manager_up_id) n LEFT JOIN paylog p on p.uuid=n.Uuid and p.payType=0 and p.payTime>? and p.payTime<? group by n.id order by totalMoney desc,createTime desc limit ?,10',[starttime,endtime,limitstart],(err,result)=>{
                                resultJson.accounts=result;
                                console.log('allalalala')
                                progress++;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                            conn.query('SELECT count(a.uuid) as totalNum FROM (select n.* from account n )a ',[starttime,endtime],(err,result)=>{
                                progress++;
                                // console.log('totalNumtotalNumtotalNum:');
                                // console.log(result);
                                resultJson.totalNum=result[0].totalNum;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                        }
                    }

                }else{
                    if(uuid){
                        var progress=0;
                        conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE a.manager_up_id = m.id and (a.manager_up_id=? or m.levelStr like ?) and a.uuid=?)n LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime<? and p.uuid=n.Uuid group by n.id ',[managerId,levelStr,uuid,starttime,endtime],(err,result)=>{
                            resultJson.accounts=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                        conn.query('SELECT count(a.uuid) as totalNum FROM account a,manager b WHERE a.manager_up_id=b.id and (a.manager_up_id=? or b.levelStr like ?) and a.uuid=?',[managerId,levelStr,uuid],(err,result)=>{
                            progress++;
                            resultJson.totalNum=result[0].totalNum;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }else{
                        var progress=0;
                        conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE a.manager_up_id = m.id and ( a.manager_up_id=? or m.levelStr like ?))n LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime<? and p.uuid=n.Uuid group by n.id order by totalMoney desc,createTime desc limit ?,10',[managerId,levelStr,starttime,endtime,limitstart],(err,result)=>{
                            resultJson.accounts=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                        conn.query('SELECT count(a.uuid) as totalNum FROM account a,manager b WHERE a.manager_up_id = b.id and (a.manager_up_id=? or b.levelStr like ?)',[managerId,levelStr],(err,result)=>{
                            progress++;
                            resultJson.totalNum=result[0].totalNum;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }

                }

            }

        })

    },
    validUuidReManagerUpId:(req,res)=>{
        if(req.session.user){
            var uuid = req.query.uuid;
            var powerId=req.session.user.power_id;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId==1){
                        conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid],(err,result)=>{
                            if(result.length>0){
                                res.json({"validuuid":1});
                            }else{
                                res.json({"validuuid":0});
                            }
                        })
                    }else{
                        res.json({"validuuid":0});
                    }
                }
                conn.release();
            })
        }
    },
    validInviteCodeReManagerUpId:(req,res)=>{
        if(req.session.user){
            var inviteCode = req.query.inviteCode;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT * FROM manager  WHERE inviteCode=? ',[inviteCode],(err,result)=>{
                        res.json(result);
                    })
                }
                conn.release();
            })
        }
    },
    reManagerUpId:(req,res)=>{
        if(req.session.user){
            var uuid=req.query.uuid;
            var managerUpId = req.query.managerUpId;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('update account set manager_up_id=? where uuid=?',[managerUpId,uuid],(err,result)=>{
                        if(result.changedRows>0){
                            res.json({"status":1})
                        }else{
                            res.json({"status":0})
                        }
                    })
                }
                conn.release();
            })
        }
    },
    vipChargeValidUuid:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var powerId=user.power_id;
            var uuid = req.query.uuid;
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
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    //所有代理都可以给任何玩家充值
                    conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid],(err,result)=>{
                        if(result.length>0){
                            res.json({"validuuid":1,"roomCard":result[0].roomCard});
                        }else{
                            res.json({"validuuid":0});
                        }
                    })
                    // if(powerId==1||powerId==5){
                    //     conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid],(err,result)=>{
                    //         if(result.length>0){
                    //             res.json({"validuuid":1,"roomCard":result[0].roomCard});
                    //         }else{
                    //             res.json({"validuuid":0});
                    //         }
                    //     })
                    // }else{
                    //     conn.query('SELECT * FROM account a,manager b  WHERE a.Uuid=? AND a.manager_up_id=b.id and (a.manager_up_id=? or  b.levelStr like ?) AND a.status!=2',[uuid,managerId,levelStr],(err,result)=>{
                    //         if(result.length>0){
                    //             res.json({"validuuid":1,"roomCard":result[0].roomCard});
                    //         }else{
                    //             res.json({"validuuid":0});
                    //         }
                    //     })
                    // }

                }
                conn.release();
            })
        }
    },
    vipCharge:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var managerId = user.id;
            var powerId = user.power_id;
            req.on("data", (buff)=> {
                var obj = qs.parse(buff.toString());
                // console.log(obj);
                var uuid=obj.uuid;
                var roomCardNum = obj.roomCardNum||0;
                var redCardNum = obj.redCardNum||0;
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        if(powerId==1){
                            conn.query('UPDATE  account SET roomCard=roomCard+? WHERE Uuid=?', [roomCardNum,uuid], (err, result)=> {
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
                                        // console.log(resu);
                                        if(resu.changedRows>0){
                                            conn.query('insert into roomcardlog values(null,?,?,?,now())',[managerId,uuid,roomCardNum],(err,result)=>{
                                                if(err){
                                                    console.log(err);
                                                }
                                            })
                                            conn.query('UPDATE account SET roomCard =roomCard+? WHERE Uuid=?',[roomCardNum,uuid],(err,resul)=>{
                                                // console.log(resul);
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
    },
    changeAccountStatus:(req,res)=>{
        if(req.session.user){
            var status = req.query.status;
            var uuid=req.query.uuid;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('update account set status=? where Uuid = ? ',[status,uuid],(err,result)=>{
                        // console.log(222);
                        // console.log(result.affectedRows);
                        res.json(result.affectedRows);
                    })
                }
                conn.release();
            })
        }
    },
    getAddVipCountDay:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            if(req.query.managerId){
                managerId=req.query.managerId;
            }
            var powerId=user.power_id;
            var resultJson=[
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0}
            ];
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    var progress=0;
                    function getcount(day){
                        var sql = `select count(id) as c from account where createTime>(CurDate()-${day}) and createTime<=(CurDate()-${day-1})`;
                        if(powerId>1||req.query.managerId){
                            sql+=`and manager_up_id=${managerId}`
                        }
                        conn.query(sql,(err,result)=>{
                            console.log(result);
                            progress++;
                            var now=new Date();
                            now.setDate(now.getDate()-day);
                            resultJson[6-day].label=now.toLocaleDateString();
                            resultJson[6-day].value=result[0].c;
                            if(progress==7){
                                // console.log(resultJson);
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }
                    for(let i=6;i>=0;i--){
                        getcount(i);
                        // console.log(123456789);
                    }
                }

            })
        }
    },
    getAddVipCountWeek:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var powerId=user.power_id;
            if(req.query.managerId){
                managerId=req.query.managerId;
            }
            var resultJson=[
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0}
            ];
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    var progress=0;
                    function getcount(month){
                        var sql = `select count(id) as c from account where createTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ${1+7*month} DAY)) and createTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ${7*month-5} DAY))`;
                        if(powerId>1||req.query.managerId){
                            sql+=`and manager_up_id=${managerId} `;
                        }
                        conn.query(sql,(err,result)=>{
                            progress++;
                            if(month==0){
                                resultJson[5-month].label='本周';
                            }else{
                                resultJson[5-month].label='上'+month+'周';
                            }
                            resultJson[5-month].value=result[0].c;
                            if(progress==6){
                                // console.log(resultJson);
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }
                    for(let i=0;i<6;i++){
                        getcount(i);
                    }
                }

            })
        }
    },
    getAddVipCountMonth:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var managerId=user.id;
            var powerId=user.power_id;
            if(req.query.managerId){
                managerId=req.query.managerId;
            }
            var resultJson=[
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0},
                {label: '', value: 0}
            ];
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    var progress=0;
                    function getcount(month){
                        var sql = `select count(id) as c from account where createTime>(SELECT concat(date_format(LAST_DAY(now() - interval ${month} month),'%Y-%m-'),'01')) and createTime<=(SELECT LAST_DAY(now() - interval ${month} month))`;
                        if(powerId>1 || req.query.managerId){
                            sql +=`and manager_up_id=${managerId}`;
                        }
                        conn.query(sql,(err,result)=>{
                            //console.log(9999999999);
                            // console.log(result);
                            progress++;
                            var now=new Date();
                            now.setMonth(now.getMonth()-month);
                            var m=parseInt(now.getMonth())+1;
                            resultJson[5-month].label=m+'月';
                            resultJson[5-month].value=result[0].c;
                            if(progress==6){
                                console.log(resultJson);
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }
                    for(let i=0;i<6;i++){
                        getcount(i);
                        // console.log(123456789);
                    }
                }

            })
        }
    }
}
