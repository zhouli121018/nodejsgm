/**
 * Created by Administrator on 2017-12-29.
 */
const pool = require('./pool');
const qs=require('querystring');

module.exports = {
    getNotes:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var status = req.query.status;
            var uuid=req.query.uuid;
            var powerId=user.power_id;
            var managerId=req.query.managerId||user.id;
            var limitstart=(req.query.page-1)*10;
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
            var resultJson={notes:[],totalNum:0,totalMoney:0};
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId>1||req.query.managerId){
                        var progress=0;
                        conn.query('select a.id,a.managerId,b.name,b.inviteCode,a.money,a.payTime,a.status from paylog a,manager b where a.managerId = b.id  and a.managerId =? and a.payTime > ? and a.payTime < ? and a.payType = 1 and a.status=1 order by a.payTime DESC limit ?,10 ',[managerId,starttime,endtime,limitstart],(err,result)=>{
                            // console.log(333);
                            progress++;
                            resultJson.notes=result;
                            if(progress==2){
                                res.json(resultJson);
                            }
                        })
                        conn.query('select count(a.id) as totalNum,IFNULL(sum(a.money),0) as totalMoney from paylog a,manager b where a.managerId = b.id  and a.managerId =? and a.payTime > ? and a.payTime < ? and a.payType = 1 and a.status=1 ',[managerId,starttime,endtime],(err,result)=>{
                            // console.log(444);
                            progress++;
                            resultJson.totalMoney=result[0].totalMoney;
                            resultJson.totalNum=result[0].totalNum;
                            if(progress==2){
                                res.json(resultJson);
                            }
                        })
                    }else{
                        var progress=0;
                        conn.query('select m.*,IFNULL(SUM(p.money),0) as money from (select * from manager where id>3)m left JOIN paylog p on p.managerId=m.id and p.payTime>? and p.payTime<? and p.payType=1 and p.status =1 GROUP BY m.id ORDER BY money desc LIMIT ?,10 ',[starttime,endtime,limitstart],(err,result)=>{
                            // console.log(333);
                            // console.log(result);
                            progress++;
                            resultJson.notes=result;
                            if(progress==2){
                                res.json(resultJson);
                            }
                        })
                        conn.query('select count(a.id) as totalNum,IFNULL(sum(a.totalMoney),0) as sumMoney from (select m.*,IFNULL(SUM(p.money),0) as totalMoney from (select * from manager where id>3)m left JOIN paylog p on p.managerId=m.id and p.payTime>? and p.payTime<? and p.payType=1 and p.status =1 GROUP BY m.id) a',[starttime,endtime],(err,result)=>{
                            // console.log(444);
                            progress++;
                            resultJson.totalMoney=result[0].sumMoney;
                            resultJson.totalNum=result[0].totalNum;
                            if(progress==2){
                                res.json(resultJson);
                            }
                        })

                    }
                }
                conn.release();
            })
        }
    }
}