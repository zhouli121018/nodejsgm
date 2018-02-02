/**
 * Created by Administrator on 2017-12-29.
 */
const pool = require('./pool');
var request = require('request');
const qs=require('querystring');

module.exports = {
    getRoomNumber:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            if(user.power_id==1){
                request({
                        url: 'http://39.106.132.18:8079/qymj/getNum?type=all',
//http://47.95.239.253:8079/qymj/getNum?type=all,http://kx.waleqp.com:8079/qymj/getNum?type=all
                        method: 'GET'
                    },
                    function(err, response, body){
                        // console.log('dangqianrenshu');
                        // console.log(body);
                        res.json(body);
                    });
            }else{
                res.json();
            }

        }
    },
    getPaylogs:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var powerId=user.power_id;
            var managerId =0;
            if(powerId==1){
                managerId=req.query.managerId;
                if(managerId){
                    var levelStr='';
                    var n=100000000;
                    var levelStr0=n+parseInt(managerId);
                    var levelStr1=levelStr0+'$%';
                    levelStr=levelStr1.slice(1);
                    if(req.query.plevelStr){
                        levelStr=req.query.plevelStr+levelStr;
                    }
                }
            }else{
                managerId=user.id;
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
            }
            var page=req.query.page;
            var limitstart=(page-1)*10;
            var limitend=10;

            // console.log('levelstr:');
            // console.log(levelStr);
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
            var resultjson={paylogs:[],totalBonus:0,totalNum:0,totalMoney:0};
            var uuid=req.query.uuid;
            var gameId=req.query.gameId;
            if(powerId==1){
                if(req.query.managerId){
                    var sql=`select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType =0 and a.status != 2 and a.payTime > '${starttime}'  and a.payTime < '${endtime}' `;
                    if(gameId){
                        sql+=` and a.gameId=${gameId}`;
                    }
                    if(uuid){
                        sql+=` and a.uuid=${uuid} `;
                    }
                    sql+=` and (b.levelStr like '${levelStr}' or b.id = ${managerId} )) n left join bonus m on n.id=m.paylogId and m.managerId=${managerId} )q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ${limitstart} ,${limitend} `;

                    var sql0=`select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > '${starttime}'  and a.payTime < '${endtime}'`;
                    if(gameId){
                        sql0+=`and a.gameId=${gameId} `;
                    }
                    if(uuid){
                        sql0+=`and a.uuid=${uuid}`;
                    }
                    sql0+=` and (b.levelStr like '${levelStr}' or b.id = ${managerId} ) ) n left join bonus m on n.id=m.paylogId and m.managerId=${managerId}`;
                }else{
                    var   sql=`select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id  and a.payType =0 and a.status != 2 and a.payTime > '${starttime}'  and a.payTime < '${endtime}'`;
                    if(gameId){
                        sql+=` and a.gameId=${gameId}`;
                    }
                    if(uuid){
                        sql+=` and a.uuid=${uuid} `;
                    }
                    sql+=` )q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ${limitstart},10 `;
                    var sql0=`select count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > '${starttime}'  and a.payTime < '${endtime}' `;
                    if(gameId){
                        sql0+=` and a.gameId=${gameId}`;
                    }
                    if(uuid){
                        sql0+=` and a.uuid=${uuid}`;
                    }

                    sql0+=`) n`;
                }
                pool.getConnection((err,conn)=>{
                    if(err){
                        console.log(err);
                    }else{
                        var progress=0;
                        conn.query(sql,(err,paylogs)=>{
                            if(paylogs){
                                resultjson.paylogs=paylogs;
                            }
                            progress++;
                            if(progress==2){
                                res.json(resultjson);
                            }
                        })
                        conn.query(sql0,(err,totalBonus)=>{
                            if(totalBonus){
                                resultjson.totalBonus=totalBonus[0].totalBonus;
                                resultjson.totalNum=totalBonus[0].totalNum;
                                resultjson.totalMoney=totalBonus[0].totalMoney;
                            }
                            progress++;
                            if(progress==2){
                                res.json(resultjson);
                            }
                        })
                    }
                    conn.release();
                })
            }else{
                var sql=`select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.status != 2 and a.payTime > '${starttime}'  and a.payTime < '${endtime}'`;
                if(gameId){
                    sql+=` and a.gameId=${gameId} `;
                }
                if(uuid){
                    sql+=` and a.uuid=${uuid}`;
                }
                sql+=` and (b.levelStr like '${levelStr}' or b.id = ${managerId} )   ) n left join bonus m on n.id=m.paylogId and m.managerId=${managerId})q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ${limitstart},${limitend}`;

                var sql0=`select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > '${starttime}' and a.payTime < '${endtime}'`;
                if(gameId){
                    sql0+=` and a.gameId=${gameId} `;
                }
                if(uuid){
                    sql0+=` and a.uuid=${uuid} `;
                }
                sql0+=` and (b.levelStr like '${levelStr}' or b.id = ${managerId} )   ) n left join bonus m on n.id=m.paylogId and m.managerId=${managerId}`;
                console.log('sql:'+sql);
                console.log('sql0:'+sql);
                pool.getConnection((err,conn)=>{
                    if(err){
                        console.log(err);
                    }else{
                        var progress=0;
                        conn.query(sql,(err,paylogs)=>{
                            if(paylogs){
                                resultjson.paylogs=paylogs;
                            }
                            progress++;
                            if(progress==2){
                                res.json(resultjson);
                            }
                        })
                        conn.query(sql0,(err,totalBonus)=>{
                            if(totalBonus){
                                resultjson.totalBonus=totalBonus[0].totalBonus;
                                resultjson.totalNum=totalBonus[0].totalNum;
                                resultjson.totalMoney=totalBonus[0].totalMoney;
                            }
                            progress++;
                            if(progress==2){
                                res.json(resultjson);
                            }
                        })
                    }
                    conn.release();
                })
            }
        }
    },
    getTotalMoneyDay:(req,res)=>{
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
                    // function getcount(day){
                        // var sql = `select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(CurDate()-${day}) and payTime <=(CurDate()-${day-1})`;
                        var sql = `select day(payTime) as label, IFNULL(sum(money),0) as value from paylog where payType=0 and status!=2 `
                        if(powerId>1||req.query.managerId){
                            sql+=`and managerId=${managerId}`;
                        }
                        sql += ` and payTime >= date(now()) - interval 6 day group by day(payTime) `
                        
                        conn.query(sql,(err,result)=>{
                            // console.log(result);
                            // progress++;
                            for(let k = 0 ;k<7;k ++){
                                var now=new Date();
                                now.setDate(now.getDate()-k);
                                console.log(now.toLocaleDateString())
                                var day = now.getDate();
                                var v = 0;
                                for(let i=0;i<result.length;i++){
                                    if(result[i].label == day){
                                        v = result[i].value;
                                        break;
                                    }
                                }
                                resultJson[6-k].label = now.toLocaleDateString();
                                resultJson[6-k].value = v;
                            }
                            console.log(resultJson);
                            res.json(resultJson);
                            
                        })
                    // }
                    // for(let i=6;i>=0;i--){
                    //     getcount(i);
                    //     // console.log(123456789);
                    // }
                }
                conn.release();
            })
        }
    },
    getTotalMoneyWeek:(req,res)=>{
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
                        var sql=`select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ${1+7*month} DAY)) and payTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ${7*month-5} DAY))`;
                        if(powerId>1||req.query.managerId){
                            sql+=`and managerId=${managerId}`;
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
                            }
                        })
                    }
                    for(let i=0;i<6;i++){
                        getcount(i);
                    }
                }
                conn.release();

            })
        }
    },
    getTotalMoneyMonth:(req,res)=>{
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
                        var sql=`select IFNULL(sum(money),0) as c from paylog where  payType=0 and status!=2 and payTime>(SELECT concat(date_format(LAST_DAY(now() - interval ${month} month),'%Y-%m-'),'01')) and payTime<=(SELECT LAST_DAY(now() - interval ${month} month))`;
                        if(powerId>1||req.query.managerId){
                            sql+=`and managerId=${managerId}`;
                        }
                        conn.query(sql,(err,result)=>{
                            progress++;
                            var now=new Date();
                            now.setMonth(now.getMonth()-month);
                            var m=parseInt(now.getMonth())+1;
                            resultJson[5-month].label=m+'月';
                            resultJson[5-month].value=result[0].c;
                            if(progress==6){
                                // console.log(resultJson);
                                res.json(resultJson);
                            }
                        })
                    }
                    for(let i=0;i<6;i++){
                        getcount(i);
                        // console.log(123456789);
                    }

                }
                conn.release();

            })
        }
    },
    getRoomcardLog:(req,res)=>{
        if(req.session.user) {
            var user = req.session.user;
            var powerId=user.power_id;
            var managerId = user.id;
            if(req.query.managerId){
                managerId=req.query.managerId;
            }
            var page=req.query.page;
            var limitstart=(page-1)*10;
            var uuid=req.query.uuid;
            console.log('uuid:'+uuid);
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
            var resultjson={roomcardLogs:[],totalNum:0,totalCard:0};
            if(powerId>1||req.query.managerId){
                if(uuid){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('select q.*,m.name from (select r.*,a.nickName,a.managerId as mid from roomcardlog r left join account a on r.accountId=a.Uuid where r.managerId=? and r.accountId=? and r.createtime>? and r.createtime<?)q left join manager m on q.managerId=m.id order by createtime desc limit ?,10', [managerId,uuid,starttime,endtime,limitstart], (err, paylogs)=> {
                                // console.log(paylogs);
                                if(paylogs){
                                    resultjson.roomcardLogs=paylogs;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }
                            });
                            conn.query('select count(n.id) as totalNum,IFNULL(sum(n.roomCard),0) as totalMoney  from(select r.* from roomcardlog r  where r.managerId=? and r.accountId=? and r.createtime>? and r.createtime<?) n  ', [managerId,uuid,starttime,endtime], (err, totalBonus)=> {
                                // console.log(11111);
                                // console.log(totalBonus);
                                if(totalBonus){
                                    resultjson.totalNum=totalBonus[0].totalNum;
                                    resultjson.totalCard=totalBonus[0].totalMoney;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }

                            });
                        }
                        conn.release();
                    });
                }else{
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('select q.*,m.name from (select r.*,a.nickName,a.managerId as mid from roomcardlog r left join account a on r.accountId=a.Uuid where r.managerId=? and r.createtime>? and r.createtime<?)q left join manager m on q.managerId=m.id order by createtime desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, paylogs)=> {
                                // console.log(paylogs);
                                if(paylogs){
                                    resultjson.roomcardLogs=paylogs;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }
                            });
                            conn.query('select count(n.id) as totalNum,IFNULL(sum(n.roomCard),0) as totalMoney  from(select r.* from roomcardlog r  where r.managerId=? and r.createtime>? and r.createtime<?) n',[managerId,starttime,endtime],(err, totalBonus)=> {
                                // console.log(11111);
                                // console.log(totalBonus);
                                if(totalBonus){
                                    resultjson.totalNum=totalBonus[0].totalNum;
                                    resultjson.totalCard=totalBonus[0].totalMoney;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }

                            });
                        }
                        conn.release();

                    });
                }
            }else{
                //res.json(resultjson);
                if(uuid){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('select q.*,m.name from (select r.*,a.nickName,a.managerId as mid from roomcardlog r left join account a on r.accountId=a.Uuid where r.accountId=? and r.createtime>? and r.createtime<?)q left join manager m on q.managerId=m.id order by createtime desc limit ?,10', [uuid,starttime,endtime,limitstart], (err, paylogs)=> {
                                // console.log(paylogs);
                                if(paylogs){
                                    resultjson.roomcardLogs=paylogs;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }
                            });
                            conn.query('select count(n.id) as totalNum,IFNULL(sum(n.roomCard),0) as totalMoney  from(select r.* from roomcardlog r  where r.accountId=? and r.createtime>? and r.createtime<?) n  ', [uuid,starttime,endtime], (err, totalBonus)=> {
                                // console.log(11111);
                                // console.log(totalBonus);
                                if(totalBonus){
                                    resultjson.totalNum=totalBonus[0].totalNum;
                                    resultjson.totalCard=totalBonus[0].totalMoney;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }

                            });
                        }
                        conn.release();

                    });
                }else{
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('select q.*,m.name from (select r.*,a.nickName,a.managerId as mid from roomcardlog r left join account a on r.accountId=a.Uuid where r.createtime>? and r.createtime<?)q left join manager m on q.managerId=m.id order by createtime desc limit ?,10', [starttime,endtime,limitstart], (err, paylogs)=> {
                                // console.log(paylogs);
                                if(paylogs){
                                    resultjson.roomcardLogs=paylogs;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }
                            });
                            conn.query('select count(n.id) as totalNum,IFNULL(sum(n.roomCard),0) as totalMoney  from(select r.* from roomcardlog r  where r.createtime>? and r.createtime<?) n',[starttime,endtime],(err, totalBonus)=> {
                                // console.log(11111);
                                // console.log(totalBonus);
                                if(totalBonus){
                                    resultjson.totalNum=totalBonus[0].totalNum;
                                    resultjson.totalCard=totalBonus[0].totalMoney;
                                }
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                }

                            });
                        }
                        conn.release();

                    });
                }
            }
        }
    },
    addBonusLog:(req,res)=>{
            req.on("data", (buff)=> {
                var obj = qs.parse(buff.toString());
                // console.log(obj);
                var paylogId = obj.paylogId;
                var paylog;
                var managerId=0;
                var money=0;
                pool.getConnection((err, conn)=> {
                    if(err){
                        console.log(err);
                    }else{
                        conn.query('select * from paylog where id =?',[paylogId],(err,result)=>{
                            if(result.length>0){
                                paylog=result[0];
                                managerId=paylog.managerId;
                                money=paylog.money;
                                conn.query('select * from manager where id=?',[managerId],(err,result0)=>{
                                    var  levelStr=result0[0].levelStr;
                                    var  levels = levelStr.split("$");
                                    var rebate0=result0[0].rebate;
                                    console.log(levelStr,levels);
                                    console.log(parseInt(levels[0]));
                                    var progress=0;
                                    conn.query('insert into bonus values(null,?,?,?)',[paylogId,managerId,money*rebate0],(err,result3)=>{
                                        if(err){console.log(err)}else console.log(result3);
                                    });
                                    for(let i=0;i<levels.length-1;i++){
                                        conn.query('select id,rebate from manager where id=?',[parseInt(levels[i])],(err,result2)=>{
                                            levels[i]=result2[0];
                                            progress++;
                                            if(progress==levels.length-1){
                                                for(let j=0;j<levels.length-1;j++){
                                                    if(j==levels.length-2){
                                                        var sql = `insert into bonus values (null,${paylogId},${levels[j].id},${money*(levels[j].rebate-rebate0)})`;
                                                        console.log(sql);
                                                        conn.query(sql);
                                                        continue;
                                                    }
                                                    conn.query('insert into bonus values(null,?,?,?)',[paylogId,levels[j].id,money*[levels[j].rebate-levels[j+1].rebate]])
                                                }
                                            }
                                        })
                                    }
                                })
                            }
                        });
                        res.json();
                    }
                    conn.release();
                })
            });
    },
    addBonusLogDoGet:(req,res)=>{
            var paylogId = req.query.paylogId;
            var paylog;
            var managerId=0;
            var money=0;
            pool.getConnection((err, conn)=> {
                if(err){
                    console.log(err);
                }else{
                    conn.query('select * from paylog where id =?',[paylogId],(err,result)=>{
                        if(result.length>0){
                            paylog=result[0];
                            managerId=paylog.managerId;
                            money=paylog.money;
                            conn.query('select * from manager where id=?',[managerId],(err,result0)=>{
                                var  levelStr=result0[0].levelStr;
                                var  levels = levelStr.split("$");
                                var rebate0=result0[0].rebate;
                                console.log(levelStr,levels);
                                console.log(parseInt(levels[0]));
                                var progress=0;
                                conn.query('insert into bonus values(null,?,?,?)',[paylogId,managerId,money*rebate0],(err,result3)=>{
                                    if(err){console.log(err)}else console.log(result3);
                                });
                                for(let i=0;i<levels.length-1;i++){
                                    conn.query('select id,rebate from manager where id=?',[parseInt(levels[i])],(err,result2)=>{
                                        levels[i]=result2[0];
                                        progress++;
                                        if(progress==levels.length-1){
                                            for(let j=0;j<levels.length-1;j++){
                                                if(j==levels.length-2){
                                                    var sql = `insert into bonus values (null,${paylogId},${levels[j].id},${money*(levels[j].rebate-rebate0)})`;
                                                    console.log(sql);
                                                    conn.query(sql);
                                                    continue;
                                                }
                                                conn.query('insert into bonus values(null,?,?,?)',[paylogId,levels[j].id,money*[levels[j].rebate-levels[j+1].rebate]])
                                            }
                                        }
                                    })
                                }
                            })
                        }
                    });
                    res.json();
                }
                conn.release();
            })
    }
}


