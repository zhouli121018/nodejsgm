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
                        url: 'http://kx.waleqp.com:8079/qymj/getNum?type=all',
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
                if(managerId){
                    if(uuid){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(gameId){
                                    conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType =0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,? ', [gameId,starttime,endtime,levelStr,managerId,uuid,managerId,limitstart,limitend], (err, paylogs)=> {
                                        //console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?   ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [gameId,starttime,endtime,levelStr,managerId,uuid,managerId], (err, totalBonus)=> {
                                        // console.log('totalBonus:');
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                }else{
                                    conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,? ', [starttime,endtime,levelStr,managerId,uuid,managerId,limitstart,limitend], (err, paylogs)=> {
                                        //console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?   ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,uuid,managerId], (err, totalBonus)=> {
                                        // console.log('totalBonus:');
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                }
                            }

                        });
                    }else{
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                // console.log(77777777777777);
                                // console.log(starttime,endtime,levelStr,managerId,limitstart,limitend,managerId);
                                if(gameId){
                                    conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,?', [gameId,starttime,endtime,levelStr,managerId,managerId,limitstart,limitend], (err, paylogs)=> {
                                        // console.log('paylogspaylogs:');
                                        // console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )    ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [gameId,starttime,endtime,levelStr,managerId,managerId], (err, totalBonus)=> {
                                        // console.log(11111);
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }

                                    });
                                }else{
                                    conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,?', [starttime,endtime,levelStr,managerId,managerId,limitstart,limitend], (err, paylogs)=> {
                                        // console.log('paylogspaylogs:');
                                        // console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )    ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,managerId], (err, totalBonus)=> {
                                        // console.log(11111);
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }

                                    });
                                }
                            }

                        });
                    }
                }else{
                    if(uuid){
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(gameId){
                                    conn.query('select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and a.payType =0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ?  and a.uuid=?)q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,? ', [gameId,starttime,endtime,uuid,limitstart,limitend], (err, paylogs)=> {
                                        // console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ?  and a.uuid=?   ) n ', [gameId,starttime,endtime,uuid], (err, totalBonus)=> {
                                        // console.log(11111);
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                }else{
                                    conn.query('select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ?  and a.uuid=?)q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,? ', [starttime,endtime,uuid,limitstart,limitend], (err, paylogs)=> {
                                        // console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ?  and a.uuid=?   ) n ', [starttime,endtime,uuid], (err, totalBonus)=> {
                                        // console.log(11111);
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                }
                            }

                        });
                    }else{
                        pool.getConnection((err, conn)=> {
                            if (err) {
                                console.log(err);
                            } else {
                                var progress=0;
                                if(gameId){
                                    conn.query('select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id  and a.payType =0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? )q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,10 ', [gameId,starttime,endtime,limitstart], (err, paylogs)=> {
                                        // console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? ) n  ', [gameId,starttime,endtime], (err, totalBonus)=> {
                                        // console.log(11111);
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }

                                    });
                                }else{
                                    conn.query('select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id  and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? )q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,10 ', [starttime,endtime,limitstart], (err, paylogs)=> {
                                        // console.log(paylogs);
                                        if(paylogs){
                                            resultjson.paylogs=paylogs;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }
                                    });
                                    conn.query('select count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? ) n  ', [starttime,endtime], (err, totalBonus)=> {
                                        // console.log(11111);
                                        // console.log(totalBonus);
                                        if(totalBonus){
                                            resultjson.totalBonus=totalBonus[0].totalBonus;
                                            resultjson.totalNum=totalBonus[0].totalNum;
                                            resultjson.totalMoney=totalBonus[0].totalMoney;
                                        }
                                        progress++;
                                        if(progress==2){
                                            res.json(resultjson);
                                            conn.release();
                                        }

                                    });
                                }
                            }

                        });
                    }
                }

            }else{
                if(uuid){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            if(gameId){
                                conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,? ', [gameId,starttime,endtime,levelStr,managerId,uuid,managerId,limitstart,limitend], (err, paylogs)=> {
                                    // console.log(paylogs);
                                    if(paylogs){
                                        resultjson.paylogs=paylogs;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?   ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [gameId,starttime,endtime,levelStr,managerId,uuid,managerId], (err, totalBonus)=> {
                                    // console.log(11111);
                                    // console.log(totalBonus);
                                    if(totalBonus){
                                        resultjson.totalBonus=totalBonus[0].totalBonus;
                                        resultjson.totalNum=totalBonus[0].totalNum;
                                        resultjson.totalMoney=totalBonus[0].totalMoney;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }
                                });
                            }else{
                                conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,? ', [starttime,endtime,levelStr,managerId,uuid,managerId,limitstart,limitend], (err, paylogs)=> {
                                    // console.log(paylogs);
                                    if(paylogs){
                                        resultjson.paylogs=paylogs;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?   ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,uuid,managerId], (err, totalBonus)=> {
                                    // console.log(11111);
                                    // console.log(totalBonus);
                                    if(totalBonus){
                                        resultjson.totalBonus=totalBonus[0].totalBonus;
                                        resultjson.totalNum=totalBonus[0].totalNum;
                                        resultjson.totalMoney=totalBonus[0].totalMoney;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }
                                });
                            }
                        }

                    });
                }else{
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            if(gameId){
                                conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,?', [gameId,starttime,endtime,levelStr,managerId,managerId,limitstart,limitend], (err, paylogs)=> {
                                    // console.log(paylogs);
                                    if(paylogs){
                                        resultjson.paylogs=paylogs;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.gameId=? and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )    ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [gameId,starttime,endtime,levelStr,managerId,managerId], (err, totalBonus)=> {
                                    // console.log(11111);
                                    // console.log(totalBonus);
                                    if(totalBonus){
                                        resultjson.totalBonus=totalBonus[0].totalBonus;
                                        resultjson.totalNum=totalBonus[0].totalNum;
                                        resultjson.totalMoney=totalBonus[0].totalMoney;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }

                                });
                            }else{
                                conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,?', [starttime,endtime,levelStr,managerId,managerId,limitstart,limitend], (err, paylogs)=> {
                                    // console.log(paylogs);
                                    if(paylogs){
                                        resultjson.paylogs=paylogs;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(m.money),0) as totalBonus,count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )    ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,managerId], (err, totalBonus)=> {
                                    // console.log(11111);
                                    // console.log(totalBonus);
                                    if(totalBonus){
                                        resultjson.totalBonus=totalBonus[0].totalBonus;
                                        resultjson.totalNum=totalBonus[0].totalNum;
                                        resultjson.totalMoney=totalBonus[0].totalMoney;
                                    }
                                    progress++;
                                    if(progress==2){
                                        res.json(resultjson);
                                        conn.release();
                                    }

                                });
                            }
                        }

                    });
                }
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
                    if(powerId>1||req.query.managerId){
                        var progress=0;
                        function getcount(day){
                            conn.query('select IFNULL(sum(money),0) as c from paylog where managerId=? and payType=0 and status!=2 and payTime>(CurDate()-?) and payTime <=(CurDate()-?)',[managerId,day,day-1],(err,result)=>{
                                // console.log(result);
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
                    }else{
                        var progress=0;
                        function getcount(day){
                            conn.query('select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(CurDate()-?) and payTime <=(CurDate()-?)',[day,day-1],(err,result)=>{
                                //console.log(9999999999);
                                // console.log(result);
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

                }

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
                    if(powerId>1||req.query.managerId){
                        var progress=0;
                        function getcount(month){
                            conn.query("select IFNULL(sum(money),0) as c from paylog where managerId=? and payType=0 and status!=2 and payTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY)) and payTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY))",[managerId,1+7*month,7*month-5],(err,result)=>{
                                //console.log(9999999999);
                                // console.log(result);
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
                    }else{
                        var progress=0;
                        function getcount(month){
                            conn.query("select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY)) and payTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY))",[1+7*month,7*month-5],(err,result)=>{
                                //console.log(9999999999);
                                // console.log(result);
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

                }

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
                    if(powerId>1||req.query.managerId){
                        var progress=0;
                        function getcount(month){
                            conn.query("select IFNULL(sum(money),0) as c from paylog where managerId=? and payType=0 and status!=2 and payTime>(SELECT concat(date_format(LAST_DAY(now() - interval ? month),'%Y-%m-'),'01')) and payTime<=(SELECT LAST_DAY(now() - interval ? month))",[managerId,month,month],(err,result)=>{
                                //console.log(9999999999);
                                // console.log(result);
                                progress++;
                                var now=new Date();
                                now.setMonth(now.getMonth()-month);
                                var m=parseInt(now.getMonth())+1;
                                resultJson[5-month].label=m+'月';
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
                            // console.log(123456789);
                        }
                    }else{
                        var progress=0;
                        function getcount(month){
                            conn.query("select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(SELECT concat(date_format(LAST_DAY(now() - interval ? month),'%Y-%m-'),'01')) and payTime<=(SELECT LAST_DAY(now() - interval ? month))",[month,month],(err,result)=>{
                                //console.log(9999999999);
                                // console.log(result);
                                progress++;
                                var now=new Date();
                                now.setMonth(now.getMonth()-month);
                                // console.log('+++++++++++++++++');
                                // console.log(month,now.getMonth());
                                var m=parseInt(now.getMonth())+1;
                                resultJson[5-month].label=m+'月';
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
                            // console.log(123456789);
                        }
                    }

                }

            })
        }
    }
}


