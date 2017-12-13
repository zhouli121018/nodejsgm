/**
 * Created by 51216 on 2017/11/22.
 */
var url = require('url');
var crypto = require('crypto');
var request = require('request');
var xml2jsparseString = require('xml2js').parseString;
const http=require('http');
const express=require('express');
const mysql=require('mysql');
const qs=require('querystring');
const fs   = require("fs");
//require('body-parser-xml')(bodyParser);
var cookieParser = require('cookie-parser');
var session = require('express-session');
//process.on('uncaughtException', function (err) {
//    //打印出错误
//    console.log(err);
//    //打印出错误的调用栈方便调试
//    console.log(err.stack);
//});
//try{
//    var ok = req.params;
//}catch(e){
//    console.log(e);
//}

var pool=mysql.createPool({
    host:'47.95.239.253',//qingyuankx 183.131.200.109 // 朝阳 47.95.239.253 //juyou 116.62.56.47 //ningdu 120.77.43.40//qingyuan120.76.100.224 //suzhou 121.196.221.247// songyuan 39.106.132.18 // qingyuan1213 103.73.206.31
    //user:'root',//mahjong
    //password:'123456',//a257joker
    user:'mahjong',
    password:'a257joker',//a257joker!@#Q
    database:'mahjong_cy',//mahjong_cy mahjong_hbe
    connectionLimit:10
});
var app=express();
var server=http.createServer(app);
server.listen(8081);
app.use(express.static('./public'));
app.use(cookieParser('sessiontest'));
app.use(session({
    secret: 'sessiontest',//与cookieParser中的一致
    resave: true,
    saveUninitialized:true
}));


var config = {
    wxappid:"wx07022b5bc486f279",//wx07022b5bc486f279 //wx0b0da56105e931d5
    mch_id:"1370897202",//  1370897202 //1481903462
    wxpaykey:"LQ0929xxfy982fjielx39093ooxx3987"// LQ0929xxfy982fjielx39093ooxx3987 //cce50ed3d4d110d68ebdc2872885c2a5
};
//生成随机字符串
function randomString(len) {
    len = len || 32;
    var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';    /****默认去掉了容易混淆的字符oOLl,9gq,Vv,Uu,I1****/
    var maxPos = $chars.length;
    var pwd = '';
    for (i = 0; i < len; i++) {
        pwd += $chars.charAt(Math.floor(Math.random() * maxPos));
    }
    return pwd;
}

function getSign(arr){
    // 按 key 值的ascll 排序
    var keys=[];
    for(var key in arr){
        keys.push(key);
    }
    keys = keys.sort();
    var newArgs = {};
    keys.forEach(function (val, key) {
        if (arr[val]){
            newArgs[val] = arr[val];
        }
    })
    var string = qs.stringify(newArgs)+'&key='+config.wxpaykey;
    // 生成签名
    return crypto.createHash('md5').update(qs.unescape(string), 'utf8').digest("hex").toUpperCase();
}


var transferUrl = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers";
function cb(){
    console.log('callbackcallback');
}
function doTransfer(openId,money,desc,ip,cb){
    var arr=[];
    arr['mch_appid']=config.wxappid;
    arr['mchid']=config.mch_id;
    arr['partner_trade_no']=randomString(32);
    arr['nonce_str']=randomString(32);
    arr['openid']=openId;
    arr['check_name']="NO_CHECK";
    arr['amount']=money*100;
    arr['desc']=desc;
    arr['spbill_create_ip']=ip;
    //console.dir(arr);
    var sign = getSign(arr);
    console.log('signsignsign:');
    console.log(sign);

    var xml = "<xml>" +
        "<mch_appid>" + config.wxappid + "</mch_appid>" +
        "<mchid>" + config.mch_id + "</mchid>" +
        "<nonce_str>" + arr['nonce_str'] + "</nonce_str>" +
        "<partner_trade_no>" + arr['partner_trade_no'] + "</partner_trade_no>" +
        "<openid>" + openId + "</openid>" +
        "<check_name>" + arr['check_name'] + "</check_name>" +
//                "<re_user_name>" + name + "</re_user_name>" +
        "<amount>" + arr['amount'] + "</amount>" +
        "<desc>" + desc + "</desc>" +
        "<sign>" + sign + "</sign>" +
        "<spbill_create_ip>"+arr['spbill_create_ip']+"</spbill_create_ip>" +
        "</xml>";

    var url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers';

    var SEND_REDPACK_URL = "https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack";
    var PFX = 'apiclient_cert.p12';
    request({
            url: url,
            method: 'POST',
            body: xml,
            agentOptions: {
                pfx: fs.readFileSync(PFX),
                passphrase: config.mch_id
            }
        },
        function(err, response, body){
            console.log(body);

        });

    //request.post({url : url, body:xml}, function (error, response, body) {
    //    cb();
    //    console.log(body);
    //    console.log(response.statusCode == 200);
    //    var prepay_id = '';
    //    if (!error && response.statusCode == 200) {
    //        // 微信返回的数据为 xml 格式， 需要装换为 json 数据， 便于使用
    //        xml2jsparseString(body, {async:true}, function (error, result) {
    //            prepay_id = result.xml.prepay_id[0];
    //            console.log('**************');
    //            console.log(result);
    //            // 放回数组的第一个元素
    //            resolve(prepay_id);
    //        });
    //    } else {
    //        console.log('+++++++++++++');
    //        reject(body);
    //    }
    //});

    //request({
    //    url: "https://api.mch.weixin.qq.com/pay/unifiedorder",
    //    method: 'POST',
    //    body: xml,
    //    agentOptions: {
    //        pfx: this.options.pfx,
    //        passphrase: config.mch_id
    //    }
    //}, function(err, response, body){
    //    console.log(body);
    //});


}
//doTransfer('oAnM9xDHgFr9UL7VRf_gu1Zml54g',1,'测试','127.0.0.1',cb);
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

                    console.log('loginlogin');
                    console.log(result);
                    if(result.length>0){
                        result[0]['msg']='登录成功！';
                        result[0]['logStatus']=1;
                        req.session.user=result[0];
                        res.json(result[0]);
                    }else{
                        res.json({msg:'用户名或密码不正确！',logStatus:0})
                    }
                    conn.release();
                })
            }
        })
    }

});

app.get('/logout',(req,res)=>{
    console.log("useruseruser:"+req.session.user);
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
//select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM account a WHERE a.manager_up_id=209)n LEFT JOIN paylog p on p.payTime>'2017-01-01' and p.payTime<'2017-11-01' and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit 0,10

//获取我的会员
app.get('/getAccount',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var powerId=user.power_id;
        var inputManagerId = req.query.managerId;
        var uuid=req.query.uuid;
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
        console.log(overTime);
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
                if(powerId==1){
                    if(inputManagerId){
                        if(uuid){
                            var progress=0;
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=? and a.uuid=?)n LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid ',[inputManagerId,uuid,starttime,endtime],(err,result)=>{
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=?)n LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit ?,10',[inputManagerId,starttime,endtime,limitstart],(err,result)=>{
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE  a.uuid=?)n LEFT JOIN paylog p on p.payTime>? and p.payType=0  and p.payTime<? and p.uuid=n.uuid group by n.uuid ',[uuid,starttime,endtime],(err,result)=>{
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=?)n LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit ?,10',[managerId,starttime,endtime,limitstart],(err,result)=>{
                                resultJson.accounts=result;
                                progress++;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                            conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE a.manager_up_id=?',[managerId],(err,result)=>{
                                progress++;
                                console.log('totalNumtotalNumtotalNum:');
                                console.log(result);
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
                        conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=? and a.uuid=?)n LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid ',[managerId,uuid,starttime,endtime],(err,result)=>{
                            resultJson.accounts=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                        conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE a.manager_up_id=? and a.uuid=?',[managerId,uuid],(err,result)=>{
                            progress++;
                            resultJson.totalNum=result[0].totalNum;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }else{
                        var progress=0;
                        conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=?)n LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit ?,10',[managerId,starttime,endtime,limitstart],(err,result)=>{
                            resultJson.accounts=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                        conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE a.manager_up_id=?',[managerId],(err,result)=>{
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
    }
});

//获取levelStr
app.get('/getlevelStr',(req,res)=>{
    if(req.session.user){
        var managerId=req.query.managerId;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                conn.query('select levelStr from manager where id=?', [managerId], (err, result)=> {
                    console.log(result);
                    res.json(result);
                });

            }
            conn.release();
        })
    }
})

//获取账单明细
app.get('/getPaylogs',(req,res)=>{
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

        console.log('levelstr:');
        console.log(levelStr);
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
        var resultjson={paylogs:[],totalBonus:0,totalNum:0,totalMoney:0};
        var uuid=req.query.uuid;
        if(powerId==1){
            if(managerId){
                if(uuid){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
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
                                console.log('totalBonus:');
                                console.log(totalBonus);
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

                    });
                }else{
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            console.log(77777777777777);
                            console.log(starttime,endtime,levelStr,managerId,limitstart,limitend,managerId);
                            conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,?', [starttime,endtime,levelStr,managerId,managerId,limitstart,limitend], (err, paylogs)=> {
                                console.log('paylogspaylogs:');
                                console.log(paylogs);
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
                                console.log(11111);
                                console.log(totalBonus);
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

                    });
                }
            }else{
                if(uuid){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ?  and a.uuid=?)q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,? ', [starttime,endtime,uuid,limitstart,limitend], (err, paylogs)=> {
                                console.log(paylogs);
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
                                console.log(11111);
                                console.log(totalBonus);
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

                    });
                }else{
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('select q.*,c.nickName from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id  and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? )q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,10 ', [starttime,endtime,limitstart], (err, paylogs)=> {
                                console.log(paylogs);
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
                                console.log(11111);
                                console.log(totalBonus);
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
                        conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b  where a.managerId = b.id and  a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid ORDER BY payTime desc limit ?,? ', [starttime,endtime,levelStr,managerId,uuid,managerId,limitstart,limitend], (err, paylogs)=> {
                            console.log(paylogs);
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
                            console.log(11111);
                            console.log(totalBonus);
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

                });
            }else{
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        var progress=0;
                        conn.query('select q.*,c.nickName from(select n.*,m.money as bonus  from(select a.*,b.inviteCode,b.name from paylog a,manager b where a.managerId = b.id and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )) n left join bonus m on n.id=m.paylogId and m.managerId=?)q left join account c on q.uuid=c.Uuid  ORDER BY payTime desc limit ?,?', [starttime,endtime,levelStr,managerId,managerId,limitstart,limitend], (err, paylogs)=> {
                            console.log(paylogs);
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
                            console.log(11111);
                            console.log(totalBonus);
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

                });
            }
        }


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
        var powerId=user.power_id;
        var uuid = req.query.uuid;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                if(powerId==1){
                    conn.query('SELECT * FROM account  WHERE Uuid=? ',[uuid,managerId],(err,result)=>{
                        if(result.length>0){
                            res.json({"validuuid":1});
                        }else{
                            res.json({"validuuid":0});
                        }
                    })
                }else{
                    conn.query('SELECT * FROM account  WHERE Uuid=? AND manager_up_id=? AND status!=2',[uuid,managerId],(err,result)=>{
                        if(result.length>0){
                            res.json({"validuuid":1});
                        }else{
                            res.json({"validuuid":0});
                        }
                    })
                }

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
        var userPowerId=user.power_id;
        var pmid=user.id;
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
            pmid = obj.pmid;
            var pwd='e10adc3949ba59abbe56e057f20f883e';
            var redCard=obj.redCard;
            var plevelStr=obj.plevelStr;
            var levelStr='';
            if(pmid>3){
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
                    conn.query('INSERT INTO manager VALUES(null,?,?,?,?,0,0,?,0,?,?,?,1,?,1,?,?,now(),?,null)', [powerId,uname,tel,pwd,pmid,inviteCode,weixin,qq,rebate,levelStr,uuid,redCard], (err, result)=> {
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
                if(powerId==1){
                    conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM account a WHERE   a.Uuid=? order by a.createTime desc', [uuid], (err, result)=> {
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
                }else{
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
            }

        })
    }
});

// searchVipByTime
app.get('/searchVipByTime',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
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
                if(powerId==1){
                    conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM account a  order by a.createTime desc',  (err, result)=> {
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
                }else{
                    conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id and a.status!=2 order by a.createTime desc', [managerId], (err, result)=> {
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

            }

        })
    }
});

//修改玩家账号状态
app.get('/changeAccountStatus',(req,res)=>{
    if(req.session.user){
        var status = req.query.status;
        var uuid=req.query.uuid;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('update account set status=? where Uuid = ? ',[status,uuid],(err,result)=>{
                    console.log(222);
                    console.log(result.affectedRows);
                    res.json(result.affectedRows);
                })
            }
            conn.release();
        })
    }
});

//获取提现流水
app.get('/getNotes',(req,res)=>{
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
        console.log(overTime);
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
                        console.log(333);
                        progress++;
                        resultJson.notes=result;
                        if(progress==2){
                            res.json(resultJson);
                        }
                    })
                    conn.query('select count(a.id) as totalNum,IFNULL(sum(a.money),0) as totalMoney from paylog a,manager b where a.managerId = b.id  and a.managerId =? and a.payTime > ? and a.payTime < ? and a.payType = 1 and a.status=1 ',[managerId,starttime,endtime],(err,result)=>{
                        console.log(444);
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
                        console.log(333);
                        console.log(result);
                        progress++;
                        resultJson.notes=result;
                        if(progress==2){
                            res.json(resultJson);
                        }
                    })
                    conn.query('select count(a.id) as totalNum,IFNULL(sum(a.totalMoney),0) as sumMoney from (select m.*,IFNULL(SUM(p.money),0) as totalMoney from (select * from manager where id>3)m left JOIN paylog p on p.managerId=m.id and p.payTime>? and p.payTime<? and p.payType=1 and p.status =1 GROUP BY m.id) a',[starttime,endtime],(err,result)=>{
                        console.log(444);
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
});

//获取下级用户数量
app.get('/getVipCount',(req,res)=>{
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
                        console.log(9999999999);
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
});

//获取下级代理数量
app.get('/getAgentCount',(req,res)=>{
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
});

//获取下级用户充值金额，计算收益
app.get('/getmineone',(req,res)=>{
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
                conn.query('select IFNULL(sum(money),0)as mineone from paylog where managerId =? and payTime > ? and payTime < ? and payType = 0  and payTime > (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and (payType = 1 or payType = 2) and status = 1)',[managerId,starttime,endtime,managerId],(err,result)=>{
                    console.log('mineone=====');
                    console.log(result);
                    req.session.mineone=(result[0].mineone)*rebate;
                    res.json({"mineone":(result[0].mineone)*rebate});
                })
            }
            conn.release();
        })
    }
});

//获取下级代理用户充值金额，计算收益
app.get('/getminetwo',(req,res)=>{
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
        console.log(overTime);
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
                conn.query('select IFNULL(sum(n.money*(?-(o.rebate+0.0))),0.0) as minetwo from (select sum(m.money) as money,m.top1mid from (select sum(a.money) as money,b.id,(case when (substring(b.levelStr,?,8)+0)=0 then b.id else (substring(b.levelStr,?,8)+0) end) as top1mid from paylog a,manager b where a.managerId = b.id  and a.payType = 0 and a.payTime > (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and payType = 1 and status = 1) and b.levelStr like ? group by id,top1mid) m group by m.top1mid) n,manager o where n.top1mid = o.id',[rebate,length,length,managerId,levelStr],(err,result)=>{
                    console.log('minetwo=====');
                    console.log(result);
                    req.session.minetwo=result[0].minetwo;
                    res.json(result[0]);
                })
            }
            conn.release();
        })
    }
});

//查询我的代理
app.get('/getMyAgents',(req,res)=>{
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
        console.log(overTime);
        if(!starttime){
            starttime='1970-01-01';
        }
        if(!endtime){
            endtime=overTime;
        }
        var inputPowerId=req.query.powerId;
        var limitstart=(req.query.page-1)*10;
        var uname=req.query.uname;
        var inviteCode=req.query.invitecode;
        console.log(starttime,endtime,uname,inviteCode);
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where manager_up_id=? and power_id=?',[managerId,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2  ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and name=? and inviteCode=? and power_id=?',[managerId,uname,inviteCode,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2  ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2  ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and name=? and power_id=?',[managerId,uname,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2  ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id )s LEFT JOIN account a ON s.id=a.managerId  and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?  and inviteCode=? and power_id=?',[managerId,inviteCode,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where id>3 and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where id>3 and power_id=?',[inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m ',(err,result)=>{
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id)o', [uname,inviteCode,inputPowerId,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('select count(m.id) as totalNum from manager m where name=? and inviteCode=? and power_id=?',[uname,inviteCode,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                    //console.log(result);
                                    resultJson.managers=result;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
                                conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and  p.payTime>? and p.payTime< ? and p.managerId=q.id)o', [uname,inviteCode,starttime,endtime], (err, result)=> {
                                    //console.log(result);
                                    resultJson.totalMoney=result[0].sumMoney;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                });
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where name=? and power_id=?',[uname,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=? and power_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,inputPowerId,starttime,endtime,limitstart], (err, result)=> {
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
                                conn.query('select count(m.id) as totalNum from manager m where inviteCode=? and power_id=?',[inviteCode,inputPowerId],(err,result)=>{
                                    resultJson.totalNum=result[0].totalNum;
                                    progress++;
                                    if(progress==3){
                                        res.json(resultJson);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,starttime,endtime,limitstart], (err, result)=> {
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
                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, result)=> {
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
                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
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
                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where name=? and manager_up_id=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,managerId,starttime,endtime,limitstart], (err, result)=> {
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
                        conn.query('select s.*,a.nickName,a.roomCard,a.redCard as bmount from(SELECT r.*,COUNT(g.id) as agentNum from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON  a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0  and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)r LEFT JOIN manager g on g.manager_up_id=r.id GROUP BY r.id)s LEFT JOIN account a ON s.id=a.managerId and a.status!=2 ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,starttime,endtime,limitstart], (err, result)=> {
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
});

//获取一周内每天新增会员数量
app.get('/getAddVipCount/day',(req,res)=>{
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
                           conn.query('select count(id) as c from account where manager_up_id=? and createTime>(CurDate()-?) and createTime<=(CurDate()-?)',[managerId,day,day-1],(err,result)=>{
                               //console.log(9999999999);
                               console.log(result);
                               progress++;
                               var now=new Date();
                               now.setDate(now.getDate()-day);
                               resultJson[6-day].label=now.toLocaleDateString();
                               resultJson[6-day].value=result[0].c;
                               if(progress==7){
                                   console.log(resultJson);
                                   res.json(resultJson);
                                   conn.release();
                               }
                           })
                       }
                       for(let i=6;i>=0;i--){
                           getcount(i);
                           console.log(123456789);
                       }
                   }else{
                       var progress=0;
                       function getcount(day){
                           conn.query('select count(id) as c from account where createTime>(CurDate()-?) and createTime<=(CurDate()-?)',[day,day-1],(err,result)=>{
                               //console.log(9999999999);
                               console.log(result);
                               progress++;
                               var now=new Date();
                               now.setDate(now.getDate()-day);
                               resultJson[6-day].label=now.toLocaleDateString();
                               resultJson[6-day].value=result[0].c;
                               if(progress==7){
                                   console.log(resultJson);
                                   res.json(resultJson);
                                   conn.release();
                               }
                           })
                       }
                       for(let i=6;i>=0;i--){
                           getcount(i);
                           console.log(123456789);
                       }
                   }

            }

        })
    }
});

//获取近六周新增会员数量
app.get('/getAddVipCount/week',(req,res)=>{
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
                        conn.query("select count(id) as c from account where manager_up_id=? and createTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY)) and createTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY))",[managerId,1+7*month,7*month-5],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
                            progress++;
                            if(month==0){
                                resultJson[5-month].label='本周';
                            }else{
                                resultJson[5-month].label='上'+month+'周';
                            }
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
                    }
                }else{
                    var progress=0;
                    function getcount(month){
                        conn.query("select count(id) as c from account where  createTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY)) and createTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY))",[1+7*month,7*month-5],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
                            progress++;
                            if(month==0){
                                resultJson[5-month].label='本周';
                            }else{
                                resultJson[5-month].label='上'+month+'周';
                            }
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
                    }
                }

            }

        })
    }
});

//获取半年内每月新增会员数量
app.get('/getAddVipCount/month',(req,res)=>{
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
                        conn.query("select count(id) as c from account where manager_up_id=? and createTime>(SELECT concat(date_format(LAST_DAY(now() - interval ? month),'%Y-%m-'),'01')) and createTime<=(SELECT LAST_DAY(now() - interval ? month))",[managerId,month,month],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
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
                        console.log(123456789);
                    }
                }else{
                    var progress=0;
                    function getcount(month){
                        conn.query("select count(id) as c from account where createTime>(SELECT concat(date_format(LAST_DAY(now() - interval ? month),'%Y-%m-'),'01')) and createTime<=(SELECT LAST_DAY(now() - interval ? month))",[month,month],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
                            progress++;
                            var now=new Date();
                            now.setMonth(now.getMonth()-month);
                            console.log('+++++++++++++++++');
                            console.log(month,now.getMonth());
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
                        console.log(123456789);
                    }
                }

            }

        })
    }
});

//获取一周内每天充值总金额
app.get('/getTotalMoney/day',(req,res)=>{
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
                            console.log(result);
                            progress++;
                            var now=new Date();
                            now.setDate(now.getDate()-day);
                            resultJson[6-day].label=now.toLocaleDateString();
                            resultJson[6-day].value=result[0].c;
                            if(progress==7){
                                console.log(resultJson);
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }
                    for(let i=6;i>=0;i--){
                        getcount(i);
                        console.log(123456789);
                    }
                }else{
                    var progress=0;
                    function getcount(day){
                        conn.query('select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(CurDate()-?) and payTime <=(CurDate()-?)',[day,day-1],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
                            progress++;
                            var now=new Date();
                            now.setDate(now.getDate()-day);
                            resultJson[6-day].label=now.toLocaleDateString();
                            resultJson[6-day].value=result[0].c;
                            if(progress==7){
                                console.log(resultJson);
                                res.json(resultJson);
                                conn.release();
                            }
                        })
                    }
                    for(let i=6;i>=0;i--){
                        getcount(i);
                        console.log(123456789);
                    }
                }

            }

        })
    }
});

//获取近六周每周充值总金额
app.get('/getTotalMoney/week',(req,res)=>{
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
                            console.log(result);
                            progress++;
                            if(month==0){
                                resultJson[5-month].label='本周';
                            }else{
                                resultJson[5-month].label='上'+month+'周';
                            }
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
                    }
                }else{
                    var progress=0;
                    function getcount(month){
                        conn.query("select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY)) and payTime<=(select date_sub(curdate(),INTERVAL WEEKDAY(curdate()) + ? DAY))",[1+7*month,7*month-5],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
                            progress++;
                            if(month==0){
                                resultJson[5-month].label='本周';
                            }else{
                                resultJson[5-month].label='上'+month+'周';
                            }
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
                    }
                }

            }

        })
    }
});

//获取半年内每月充值总金额
app.get('/getTotalMoney/month',(req,res)=>{
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
                            console.log(result);
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
                        console.log(123456789);
                    }
                }else{
                    var progress=0;
                    function getcount(month){
                        conn.query("select IFNULL(sum(money),0) as c from paylog where payType=0 and status!=2 and payTime>(SELECT concat(date_format(LAST_DAY(now() - interval ? month),'%Y-%m-'),'01')) and payTime<=(SELECT LAST_DAY(now() - interval ? month))",[month,month],(err,result)=>{
                            //console.log(9999999999);
                            console.log(result);
                            progress++;
                            var now=new Date();
                            now.setMonth(now.getMonth()-month);
                            console.log('+++++++++++++++++');
                            console.log(month,now.getMonth());
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
                        console.log(123456789);
                    }
                }

            }

        })
    }
});

//获取代理上次提现剩余的收益
app.get('/getRemain',(req,res)=>{
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
                        console.log('remainremain');
                        console.log(result);
                        if(result.length>0){
                            req.session.remain=result[0].money;
                        }else{
                            req.session.remain=0;
                        }
                        console.log('req.session.remain'+req.session.remain);
                        //req.session.remain=result[0].money||0;
                        res.json(result);
                    }
                })
            }
            conn.release();
        })
    }
});

//代理提现
app.post('/tixian',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.id;
        var uuid = user.uuid;
        var powerId = user.power_id;
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            console.log(obj);
            var ip=obj.ip;
            var money = parseFloat(obj.money);
            var totalBonus=parseFloat(req.session.mineone)+parseFloat(req.session.minetwo)+parseFloat(req.session.remain);
            if(req.session[managerId]&&req.session[managerId].day==new Date().toLocaleDateString()&&req.session[managerId].times>=2){
                res.json({"status":0,"msg":"一天只能提现2次，如有疑问请联系管理员！"});
                return;
            }
            if(money>0){
                if(money>totalBonus){
                    res.json({"status":0,"msg":"提现金额超出收益，如有疑问请联系管理员！"});
                }else if(money>5000){
                    res.json({"status":0,"msg":"单次提现金额不超过5000元，如有疑问请联系管理员！"});
                }else if(money<100){
                    res.json({"status":0,"msg":"提现金额不足100元！"});
                }else{
                    pool.getConnection((err, conn)=> {
                        conn.query('INSERT INTO paylog VALUES (null,?,?,?,0,now(),1,1,0,3)',[managerId,uuid,money],(err,result)=>{
                            if (err) {
                                console.log(err);
                            } else {
                                console.log('paylogpaylog');
                                console.log(result);
                                var insertId=0;
                                if(result.affectedRows>0){
                                    insertId=result.insertId;
                                    conn.query('INSERT INTO paylog VALUES (null,?,?,?,0,now(),9,1,0,0)',[managerId,uuid,totalBonus-money],(err,result)=>{
                                        if (err) {
                                            console.log(err);
                                        } else {
                                            if(result.affectedRows>0){
                                                conn.query('select openid from account where Uuid = ? and status!=2',[uuid],(err,result)=>{
                                                    if(result.length>0){
                                                        doTransfer(result[0].openid,money,'代理提现',ip,cb);
                                                        console.log('openid'+result[0].openid);
                                                        if(req.session[managerId]&&req.session[managerId].day==new Date().toLocaleDateString()){
                                                            req.session[managerId]={day:new Date().toLocaleDateString(),times:2};
                                                        }else{
                                                            req.session[managerId]={day:new Date().toLocaleDateString(),times:1};
                                                        }

                                                        console.log(req.session[managerId]);
                                                        res.json({"status":1,"msg":"你的提现人民币"+money+"元的请求已经发出！请留意你的微信转账记录！"})

                                                    }
                                                })

                                            }
                                        }
                                    })
                                }
                            }
                        })
                        conn.release();
                    })
                }
            }else{
                res.json({"status":0,"msg":"请输入正确的提现金额！"})
            }


        });


    }
});
