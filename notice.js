/**
 * Created by Administrator on 2017-12-29.
 */
const pool = require('./pool');
const qs=require('querystring');

module.exports ={
    getAllNotice:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var powerId=user.power_id;
            var type=req.query.type;
            var limitstart=(req.query.page-1)*10;
            var starttime=req.query.starttime;
            var endtime=req.query.endtime;
            var now=new Date();
            now.setDate(now.getDate()+30);
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
            var resultJson={notices:[],totalNum:0};
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    if(powerId==1){
                        var progress=0;
                        if(type){
                            conn.query('select * from noticetable where startTime>=? and endTime < ? and type=? order by createTime desc limit ?,10',[starttime,endtime,type,limitstart],(err,result)=>{
                                progress++;
                                resultJson.notices=result;
                                if(progress==2){
                                    res.json(resultJson);
                                }
                            });
                            conn.query('select count(id) as m from noticetable where startTime>=? and endTime < ? and type=?',[starttime,endtime,type],(err,result)=>{
                                progress++;
                                resultJson.totalNum=result[0].m;
                                if(progress==2){
                                    res.json(resultJson);
                                }
                            })
                        }else{
                            conn.query('select * from noticetable where startTime>=? and endTime < ? order by createTime desc limit ?,10',[starttime,endtime,limitstart],(err,result)=>{
                                progress++;
                                resultJson.notices=result;
                                if(progress==2){
                                    res.json(resultJson);
                                }
                            });
                            conn.query('select count(id) as m from noticetable where startTime>=? and endTime < ?',[starttime,endtime],(err,result)=>{
                                progress++;
                                resultJson.totalNum=result[0].m;
                                if(progress==2){
                                    res.json(resultJson);
                                }
                            })
                        }

                    }
                }
                conn.release();
            })
        }
    },
    addNotice:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var powerId=user.power_id;
            var managerId=0;
            if(req.query.managerId){
                managerId=req.query.managerId;
            }else{
                managerId=null;
            }
            var type=req.query.type;
            var content=req.query.content;
            var startTime=req.query.startTime;
            var endTime=req.query.endTime;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{

                    conn.query('insert into noticetable values(null,?,?,?,2,now(),?,?)',[content,type,managerId,startTime,endTime],(err,result)=>{
                        // console.log(result);
                        if(result.affectedRows>0){
                            res.json({"status":1});
                        }else{
                            res.json({"status":0});
                        }
                    })

                }
                conn.release();
            })
        }
    },
    editNotice:(req,res)=>{
        if(req.session.user){
            var user=req.session.user;
            var powerId=user.power_id;
            var managerId=0;
            if(req.query.managerId){
                managerId=req.query.managerId;
            }else{
                managerId=null;
            }
            var nid=req.query.nid;
            var type=req.query.type;
            var content=req.query.content;
            var startTime=req.query.startTime;
            var endTime=req.query.endTime;
            pool.getConnection((err,conn)=>{
                if(err){
                    console.log(err);
                }else{
                    conn.query('update noticetable set content=?,type=?,startTime=?,endTime=?,managerId=? where id=?',[content,type,startTime,endTime,managerId,nid],(err,result)=>{
                        // console.log(result);
                        if(result.changedRows>0){
                            res.json({"status":1});
                        }else{
                            res.json({"status":0});
                        }
                    })

                }
                conn.release();
            })
        }
    }
}
