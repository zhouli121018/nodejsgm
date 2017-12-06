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
server.listen(8081);
app.use(express.static('./public'));
app.use(cookieParser('sessiontest'));
app.use(session({
    secret: 'sessiontest',//与cookieParser中的一致
    resave: true,
    saveUninitialized:true
}));



var config = {
    wxappid:"wx0b0da56105e931d5",//wx07022b5bc486f279
    mch_id:"1481903462",//  1370897202
    wxpaykey:"cce50ed3d4d110d68ebdc2872885c2a5"// LQ0929xxfy982fjielx39093ooxx3987
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

//获取微信支付的签名
//function getSign(signParams){
//    // 按 key 值的ascll 排序
//    var keys = Object.keys(signParams);
//    keys = keys.sort();
//    var newArgs = {};
//    keys.forEach(function (val, key) {
//        if (signParams[val]){
//            newArgs[val] = signParams[val];
//        }
//    })
//    var string = queryString.stringify(newArgs)+'&key='+config.wxpaykey;
//    // 生成签名
//    return crypto.createHash('md5').update(queryString.unescape(string), 'utf8').digest("hex").toUpperCase();
//}

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
    console.log('--------------------');
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
    var PFX = '/root/apiclient_cert.p12';
    request({
            url: url,
            method: 'POST',
            body: xml,
            //agentOptions: {
            //    pfx: fs.readFileSync(PFX),
            //    passphrase: config.mch_id
            //}
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
doTransfer('oAnM9xDHgFr9UL7VRf_gu1Zml54g',1,'测试','127.0.0.1',cb);



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
app.get('/getNextManagers',(req,res)=>{
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
        var uname=req.query.uname;
        var inviteCode=req.query.invitecode;
        console.log(starttime,endtime,uname,inviteCode);
        if(powerId==1){
            if(req.query.managerId){
                if(!uname&&!inviteCode){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId and a.status!=2', [managerId], (err, result)=> {
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
            }else{
                if(!uname&&!inviteCode){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId and a.status!=2', [managerId], (err, result)=> {
                                console.log(888888,managerId);
                                console.log(result);
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
                            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE  m.id = a.managerId and m.name=? and m.inviteCode=?', [uname,inviteCode], (err, result)=> {
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
                            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE  m.id = a.managerId and m.name=? ', [uname], (err, result)=> {
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
                            conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE  m.id = a.managerId and m.inviteCode=?', [inviteCode], (err, result)=> {
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

        }else{
            if(!uname&&!inviteCode){
                pool.getConnection((err, conn)=> {
                    if (err) {
                        console.log(err);
                    } else {
                        conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE m.manager_up_id=? and m.id = a.managerId and a.status!=2', [managerId], (err, result)=> {
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=? and a.uuid=?)n LEFT JOIN paylog p on p.payType=0 and p.status=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid ',[inputManagerId,uuid,starttime,endtime],(err,result)=>{
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=?)n LEFT JOIN paylog p on p.payType=0 and p.status=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit ?,10',[inputManagerId,starttime,endtime,limitstart],(err,result)=>{
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE  a.uuid=?)n LEFT JOIN paylog p on p.payTime>? and p.payType=0 and p.status=0 and p.payTime<? and p.uuid=n.uuid group by n.uuid ',[uuid,starttime,endtime],(err,result)=>{
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
                            conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=? )n LEFT JOIN paylog p on p.payType=0 and p.status=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit ?,10',[managerId,starttime,endtime,limitstart],(err,result)=>{
                                resultJson.accounts=result;
                                progress++;
                                if(progress==2){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            })
                            conn.query('SELECT count(a.uuid) as totalNum FROM account a WHERE a.manager_up_id=?',[managerId],(err,result)=>{
                                progress++;
                                console.log(111111111111111111111111);
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
                        conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=? and a.uuid=?)n LEFT JOIN paylog p on p.payType=0 and p.status=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid ',[managerId,uuid,starttime,endtime],(err,result)=>{
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
                        conn.query('select n.*,IFNULL(sum(p.money),0) as totalMoney from(SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime,a.manager_up_id FROM account a WHERE a.manager_up_id=?)n LEFT JOIN paylog p on p.payType=0 and p.status=0 and p.payTime>? and p.payTime<? and p.uuid=n.uuid group by n.uuid order by totalMoney desc limit ?,10',[managerId,starttime,endtime,limitstart],(err,result)=>{
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
app.get('/getAccounts',(req,res)=>{
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
         pool.getConnection((err, conn)=> {
                if (err) {
                    console.log(err);
                } else {
                    if(powerId==1){
                        if(inputManagerId){
                            if(uuid){
                                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id and a.Uuid=?', [inputManagerId,uuid], (err, result)=> {
                                    if(result.length>0) {
                                        var progress = 0;
                                        for (let account of result) {
                                            conn.query('select IFNULL(sum(p.money),0) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime>? and p.payTime< ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                                console.log(sum);
                                                account['sumMoney'] = sum[0].m;
                                                progress++;
                                                if(progress==result.length){
                                                    res.json(result);
                                                    conn.release();
                                                }
                                            })
                                        }
                                    }else{
                                        res.json(result);
                                        conn.release();
                                    }
                                })
                            }else{
                                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id  order by a.createTime desc ', [inputManagerId], (err, result)=> {
                                    //console.log(result);
                                    if(result.length>0) {
                                        var progress = 0;
                                        for (let account of result) {
                                            conn.query('select IFNULL(sum(p.money),0) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime>? and p.payTime< ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                                console.log(sum);
                                                account['sumMoney'] = sum[0].m;
                                                progress++;
                                                if(progress==result.length){
                                                    res.json(result);
                                                    conn.release();
                                                }
                                            })
                                        }
                                    }else{
                                        res.json(result);
                                        conn.release();
                                    }

                                })

                            }
                        }else{
                            if(uuid){
                                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM account a WHERE a.uuid=?',[uuid], (err, result)=> {
                                    //console.log(result);
                                    if(result.length>0) {
                                        var progress = 0;
                                        for (let account of result) {
                                            conn.query('select IFNULL(sum(p.money),0) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime>? and p.payTime< ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                                console.log(sum);
                                                account['sumMoney'] = sum[0].m;
                                                progress++;
                                                if(progress==result.length){
                                                    res.json(result);
                                                    conn.release();
                                                }
                                            })
                                        }
                                    }else{
                                        res.json(result);
                                        conn.release();
                                    }

                                })
                            }else{
                                conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM account a  order by a.createTime desc', (err, result)=> {
                                    //console.log(result);
                                    console.log(666);
                                    if(result.length>0) {
                                        var progress = 0;
                                        for (let account of result) {
                                            conn.query('select IFNULL(sum(p.money),0) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime>? and p.payTime< ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                                console.log(sum);
                                                account['sumMoney'] = sum[0].m;
                                                progress++;
                                                if(progress==result.length){
                                                    res.json(result);
                                                    conn.release();
                                                }
                                            })
                                        }
                                    }else{
                                        res.json(result);
                                        conn.release();
                                    }
                                })

                            }
                        }

                    }else{
                        if(uuid){
                            conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id and a.Uuid=? and a.status!=2', [managerId,uuid], (err, result)=> {
                                //console.log(result);
                                if(result.length>0) {
                                    var progress = 0;
                                    for (let account of result) {
                                        conn.query('select IFNULL(sum(p.money),0) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime>? and p.payTime< ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                            console.log(sum);
                                            account['sumMoney'] = sum[0].m;
                                            progress++;
                                            if(progress==result.length){
                                                res.json(result);
                                                conn.release();
                                            }
                                        })
                                    }
                                }else{
                                    res.json(result);
                                    conn.release();
                                }

                            })

                        }else{
                            conn.query('SELECT a.uuid,a.nickName,a.roomCard,a.redCard,a.status,a.createTime FROM manager m,account a WHERE a.manager_up_id=? and m.id = a.manager_up_id  and a.status!=2  order by a.createTime desc', [managerId], (err, result)=> {
                                //console.log(result);
                                if(result.length>0) {
                                    var progress = 0;
                                    for (let account of result) {
                                        conn.query('select IFNULL(sum(p.money),0) as m from paylog p where p.payType=0 and p.status = 1 and p.uuid =? and p.payTime>? and p.payTime< ?', [account.uuid,starttime,endtime], (err, sum)=> {
                                            console.log(sum);
                                            account['sumMoney'] = sum[0].m;
                                            progress++;
                                            if(progress==result.length){
                                                res.json(result);
                                                conn.release();
                                            }
                                        })
                                    }
                                }else{
                                    res.json(result);
                                    conn.release();
                                }

                            })

                        }

                    }

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
                var plevelStr='';
                plevelStr=user.levelStr;
                if(plevelStr){
                    levelStr=plevelStr+levelStr;
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
                            conn.query('select n.*,m.money as bonus  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ORDER BY payTime desc limit ?,? ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,uuid,limitstart,limitend,managerId], (err, paylogs)=> {
                                console.log(paylogs);
                                resultjson.paylogs=paylogs;
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
                            conn.query('select n.*,m.money as bonus  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )   ORDER BY payTime desc limit ?,? ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,limitstart,limitend,managerId], (err, paylogs)=> {
                                console.log(paylogs);
                                resultjson.paylogs=paylogs;
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
                            conn.query('select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ?  and a.uuid=?  ORDER BY payTime desc limit ?,? ', [starttime,endtime,uuid,limitstart,limitend], (err, paylogs)=> {
                                console.log(paylogs);
                                resultjson.paylogs=paylogs;
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
                            conn.query('select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ?    ORDER BY payTime desc limit ?,? ', [starttime,endtime,limitstart,limitend], (err, paylogs)=> {
                                console.log(paylogs);
                                resultjson.paylogs=paylogs;
                                progress++;
                                if(progress==2){
                                    res.json(resultjson);
                                    conn.release();
                                }
                            });
                            conn.query('select count(n.id) as totalNum,IFNULL(sum(n.money),0) as totalMoney  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ?    ) n  ', [starttime,endtime], (err, totalBonus)=> {
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
                        conn.query('select n.*,m.money as bonus  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? ) and a.uuid=?  ORDER BY payTime desc limit ?,? ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,uuid,limitstart,limitend,managerId], (err, paylogs)=> {
                            console.log(paylogs);
                            resultjson.paylogs=paylogs;
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
                        conn.query('select n.*,m.money as bonus  from(select a.*,b.inviteCode,c.nickName from paylog a,manager b,account c  where a.managerId = b.id and a.uuid = c.Uuid and a.payType = 0 and a.status != 2 and a.payTime > ?  and a.payTime < ? and (b.levelStr like ? or b.id = ? )   ORDER BY payTime desc limit ?,? ) n left join bonus m on n.id=m.paylogId and m.managerId=?', [starttime,endtime,levelStr,managerId,limitstart,limitend,managerId], (err, paylogs)=> {
                            console.log(paylogs);
                            resultjson.paylogs=paylogs;
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
                var progress=0;
                conn.query('select a.id,b.name,b.inviteCode,a.money,a.payTime,a.status from paylog a,manager b where a.managerId = b.id  and a.managerId =? and a.payTime > ? and a.payTime < ? and a.payType = 1 and a.status=1 order by a.payTime DESC limit ?,10 ',[managerId,starttime,endtime,limitstart],(err,result)=>{
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
            }
            conn.release();
        })
    }
});


//获取单级代理
app.get('/getNextAgents',(req,res)=>{
    if(req.session.user) {
        var user = req.session.user;
        var managerId = user.managerId;
        var powerId=user.power_id;
        pool.getConnection((err, conn)=> {
            if (err) {
                console.log(err);
            } else {
                if(powerId==1){
                    conn.query('SELECT m.*,a.uuid,a.nickName,a.roomCard,a.redCard FROM manager m,account a WHERE  and m.id = a.managerId', [managerId], (err, result)=> {
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

                }else{
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


            }
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
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('select COUNT(a.id) as vipCount from account a ,manager b where a.manager_up_id = b.id and (a.manager_up_id = ? or  b.levelStr like ?)',[managerId,levelStr],(err,result)=>{
                    //console.log(9999999999);
                    //console.log(result);
                    res.json(result[0]);
                })
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
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('select COUNT(m.id) as agentCount from manager m WHERE m.manager_up_id=?',[managerId],(err,result)=>{
                    //console.log(9999999999);
                    //console.log(result);
                    res.json(result[0]);
                })
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
                conn.query('select IFNULL(sum(money),0)as mineone from paylog where managerId =? and payTime > ? and payTime < ? and payType = 0 and status%10 = 0  and (gameId = 1 or gameId = 3)and payTime > (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and (payType = 1 or payType = 2) and status = 1)',[managerId,starttime,endtime,managerId],(err,result)=>{
                    console.log('mineone=====');
                    console.log(result);
                    res.json(result[0]);
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
                conn.query('select IFNULL(sum(n.money*(?-(o.rebate+0.0))),0.0) as minetwo from (select sum(m.money) as money,m.top1mid from (select sum(a.money) as money,b.id,(case when (substring(b.levelStr,?,8)+0)=0 then b.id else (substring(b.levelStr,?,8)+0) end) as top1mid from paylog a,manager b where a.managerId = b.id and (a.gameId = 1 or a.gameId = 3) and a.payType = 0 and a.payTime > (select IFNULL(MAX(payTime),from_unixtime(0)) from paylog where managerId = ? and payType = 1 and status = 1) and b.levelStr like ? group by id,top1mid) m group by m.top1mid) n,manager o where n.top1mid = o.id',[rebate,length,length,managerId,levelStr],(err,result)=>{
                    console.log('minetwo=====');
                    console.log(result);
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
        var limitstart=req.query.page;
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
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o  ', [managerId,starttime,endtime], (err, result)=> {
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
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,uname,inviteCode,starttime,endtime], (err, result)=> {
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
                    })
                }else if(uname&&!inviteCode){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from (SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o ', [managerId,uname,starttime,endtime], (err, result)=> {
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
                    })
                }else if(inviteCode&&!uname){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [managerId,inviteCode,starttime,endtime], (err, result)=> {
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
                    })
                }
            }else{
                if(!uname&&!inviteCode){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where id>3) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where id>3) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [starttime,endtime], (err, result)=> {
                                //console.log(result);
                                resultJson.totalMoney=result[0].sumMoney;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select count(m.id) as totalNum from manager m where id>3',(err,result)=>{
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
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where name=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id)o', [uname,inviteCode,starttime,endtime], (err, result)=> {
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
                    })
                }else if(uname&&!inviteCode){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where name=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o', [uname,starttime,endtime], (err, result)=> {
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
                    })
                }else if(inviteCode&&!uname){
                    pool.getConnection((err, conn)=> {
                        if (err) {
                            console.log(err);
                        } else {
                            var progress=0;
                            conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10',[inviteCode,starttime,endtime,limitstart], (err, result)=> {
                                //console.log(result);
                                resultJson.managers=result;
                                progress++;
                                if(progress==3){
                                    res.json(resultJson);
                                    conn.release();
                                }
                            });
                            conn.query('select IFNULL(sum(o.totalMoney),0) as sumMoney from(SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id)o',[inviteCode,starttime,endtime], (err, result)=> {
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
                        conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,starttime,endtime,limitstart], (err, result)=> {
                            //console.log(result);
                            resultJson.managers=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        });
                        conn.query('select count(m.id) as totalNum from manager m where manager_up_id=?',[managerId],(err,result)=>{
                            resultJson.totalNum=result[0].totalNum;
                            progress++;
                            if(progress==2){
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
                        conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and name=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,uname,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                            //console.log(result);
                            resultJson.managers=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        });
                        conn.query('select count(m.id) as totalNum from manager m where manager_up_id=? and name=? and inviteCode=?',[managerId,uname,inviteCode],(err,result)=>{
                            resultJson.totalNum=result[0].totalNum;
                            progress++;
                            if(progress==2){
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
                        conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where name=? and manager_up_id=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [uname,managerId,starttime,endtime,limitstart], (err, result)=> {
                            //console.log(result);
                            resultJson.managers=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        });
                        conn.query('select count(m.id) as totalNum from manager m where name=? and manager_up_id=?',[uname,managerId],(err,result)=>{
                            resultJson.totalNum=result[0].totalNum;
                            progress++;
                            if(progress==2){
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
                        conn.query('SELECT q.*,IFNULL(sum(p.money),0) as totalMoney from(select m.*,a.roomCard,a.redCard as bmount,a.nickName,a.Uuid,count(a.id) as userCounts from (select * from manager where manager_up_id=? and inviteCode=?) m left JOIN account a ON a.managerId=m.id and a.manager_up_id=m.id GROUP BY m.id )q LEFT JOIN paylog p on p.payType=0 and (p.gameId=0 or p.gameId=3) and p.payTime>? and p.payTime< ? and p.managerId=q.id GROUP BY q.id ORDER BY totalMoney desc,userCounts desc limit ?,10', [managerId,inviteCode,starttime,endtime,limitstart], (err, result)=> {
                            //console.log(result);
                            resultJson.managers=result;
                            progress++;
                            if(progress==2){
                                res.json(resultJson);
                                conn.release();
                            }
                        });
                        conn.query('select count(m.id) as totalNum from manager m where manager_up_id=? and inviteCode=?',[managerId,inviteCode],(err,result)=>{
                            resultJson.totalNum=result[0].totalNum;
                            progress++;
                            if(progress==2){
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
