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
            if(inputManagerId){
                var n=100000000;
                var levelStr0=n+parseInt(inputManagerId);
                var levelStr1=levelStr0+'$%';
                levelStr=levelStr1.slice(1);
                plevelStr=req.query.plevelStr;
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
            if(powerId==1){
                if(inputManagerId){
                    var sql= `SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE a.manager_up_id = m.id and (a.manager_up_id=${inputManagerId} or m.levelStr like '${levelStr}') `;
                    if(uuid){
                    sql+=` and a.uuid=${uuid}`;
                    }
                    sql+=` and a.createTime>'${starttime}' and a.createTime<'${endtime}' order by  roomCard desc,createTime desc limit ${limitstart},10`;
                    var sqln = `SELECT count(a.uuid) as totalNum FROM account a,manager b WHERE a.manager_up_id=b.id and (a.manager_up_id=${inputManagerId} or b.levelStr like '${levelStr}') and a.createTime>'${starttime}' and a.createTime<'${endtime}'`;
                    if(uuid){
                            sqln+=` and a.uuid=${uuid}`;
                    }
                }else{
                    var sql = `SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE a.id>0 and a.createTime>'${starttime}' and a.createTime<'${endtime}'`
                    if(uuid){
                        sql+=` and a.Uuid=${uuid}`;
                    }
                    sql+=` order by  roomCard desc,createTime desc limit ${limitstart},10`;
                    var sqln = `SELECT count(a.uuid) as totalNum FROM account a WHERE a.id>0 and a.createTime>'${starttime}' and a.createTime<'${endtime}'`;
                        if(uuid){
                            sqln +=` and a.uuid=${uuid}`;
                        }
                }
               
            }else{
                var sql= `SELECT a.*,m.name,m.power_id FROM account a left join manager m on m.id=a.manager_up_id WHERE a.manager_up_id = m.id and (a.manager_up_id=${managerId} or m.levelStr like '${levelStr}') and a.createTime>'${starttime}' and a.createTime<'${endtime}'`;
                    if(uuid){
                    sql+=` and a.uuid=${uuid}`;
                    }
                    sql+=` order by  roomCard desc,createTime desc limit ${limitstart},10`;
                    var sqln = `SELECT count(a.uuid) as totalNum FROM account a,manager b WHERE a.manager_up_id=b.id and (a.manager_up_id=${managerId} or b.levelStr like '${levelStr}') and a.createTime>'${starttime}' and a.createTime<'${endtime}'`;
                if(uuid){
                        sqln+=` and a.uuid=${uuid}`;
                }
            }

            pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    var progress=0;
                    console.log("sql:"+sql);
                    console.log("sqln:"+sqln);
                    conn.query(sql,(err,result)=>{
                        if(err){
                            console.log(err);
                        }else{
                            resultJson.accounts=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        }
                    })
                    conn.query(sqln,(err,result)=>{
                        if(err){
                            console.log(err);
                        }else{
                            progress++;
                            resultJson.totalNum=result[0].totalNum;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        }
                    })
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
                    if(powerId==1){
                        conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid,managerId],(err,result)=>{
                            if(result.length>0){
                                res.json({"validuuid":1,"roomCard":result[0].roomCard});
                            }else{
                                res.json({"validuuid":0});
                            }
                        })
                    }else{
                        conn.query('SELECT * FROM account a,manager b  WHERE a.Uuid=? AND a.manager_up_id=b.id and (a.manager_up_id=? or  b.levelStr like ?) AND a.status!=2',[uuid,managerId,levelStr],(err,result)=>{
                            if(result.length>0){
                                res.json({"validuuid":1,"roomCard":result[0].roomCard});
                            }else{
                                res.json({"validuuid":0});
                            }
                        })
                    }

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
                            conn.query('UPDATE  account SET roomCard=roomCard+?,redCard=redCard+?  WHERE Uuid=?', [roomCardNum,redCardNum,uuid], (err, result)=> {
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
                                if(result[0].roomCard<roomCardNum||result[0].redCard<redCardNum){
                                    res.json({"status": 0});
                                }else{
                                    conn.query('UPDATE account SET roomCard =roomCard-?,redCard=redCard-? WHERE managerId=?',[roomCardNum,redCardNum,managerId],(err,resu)=>{
                                        // console.log(resu);
                                        if(resu.changedRows>0){
                                            conn.query('insert into roomcardlog values(null,?,?,?,now())',[managerId,uuid,roomCardNum],(err,result)=>{
                                                if(err){
                                                    console.log(err);
                                                }
                                            })
                                            conn.query('UPDATE account SET roomCard =roomCard+?,redCard=redCard+? WHERE Uuid=?',[roomCardNum,redCardNum,uuid],(err,resul)=>{
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
    },
    validManagerId:(req,res)=>{
        if(req.session.user){
            var managerId = req.query.managerId;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('SELECT * FROM manager  WHERE id=? ',[managerId],(err,result)=>{
                        if(result.length>0){
                            res.json({"status":1,"levelStr":result[0].levelStr});
                        }else{
                            res.json({"status":0});
                        }
                    })
                }
                conn.release();
            })
        }
    },
}
