/**
 * Created by Administrator on 2017-12-29.
 */
var request = require('request');
const pool = require('./pool');
const fs   = require("fs");
var xml2jsparseString = require('xml2js').parseString;
const qs=require('querystring');
var crypto = require('crypto');

var config = {
    wxappid:"wxb4bccad23ef9a324",//wx07022b5bc486f279 //wx0b0da56105e931d5 // wxb4bccad23ef9a324
    mch_id:"1493104312",//  1370897202 //1481903462 // 1493104312
    wxpaykey:"LQsy29dfwerxoiekxi302k3i192lso2k"// LQ0929xxfy982fjielx39093ooxx3987 //cce50ed3d4d110d68ebdc2872885c2a5 //LQsy29dfwerxoiekxi302k3i192lso2k
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
    console.log('代理提现');
}
  function  doTransfer(openId,money,desc,ip,cb){
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
    var sign = getSign(arr);

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
            console.log(err);
            console.log(response);
            console.log(body);
            var str=body;
            var n=str.indexOf('<result_code><![CDATA[');
            var m=str.indexOf(']]></result_code>');
            var str0=str.slice(n+parseInt(('<result_code><![CDATA['.length)),m);
            console.log(str0);
            if(str0=='SUCCESS'){
                cb();
            }
        });
}
// doTransfer('oDNB60Ra7ft7Jtck284kiMLhBaAI',1,'提现','127.0.0.1',cb)
module.exports = {
    tixian:(req,res)=>{
        var user = req.session.user;
        var managerId = user.id;
        var uuid = user.uuid;
        var powerId = user.power_id;
        req.on("data", (buff)=> {
            var obj = qs.parse(buff.toString());
            // console.log(obj);
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
                }
                else if(money<100){
                    res.json({"status":0,"msg":"提现金额不足100元！"});
                }
                else{
                    pool.getConnection((err, conn)=> {
                        conn.query('INSERT INTO paylog VALUES (null,?,?,?,0,now(),1,0,0,0)',[managerId,uuid,money],(err,result)=>{
                            if (err) {
                                console.log(err);
                            } else {
                                // console.log('paylogpaylog');
                                // console.log(result);
                                var insertId=0;
                                if(result.affectedRows>0){
                                    var m=totalBonus-money;
                                    insertId=result.insertId;
                                    function insertremain(managerId,uuid,m){
                                        conn.query('update paylog set status=1 where id=?',[insertId]);
                                        conn.query('INSERT INTO paylog VALUES (null,?,?,?,0,now(),9,1,0,0)',[managerId,uuid,m],(err,result)=>{
                                            if (err) {
                                                console.log(err);
                                            }
                                        })
                                    }
                                    conn.query('select openid from account where Uuid = ? and status!=2',[uuid],(err,result)=>{
                                        if(result.length>0){
                                            function ab(){
                                                insertremain(managerId,uuid,m);
                                            };
                                            doTransfer(result[0].openid,money,'代理提现',ip,ab);
                                            console.log('openid'+result[0].openid);
                                            if(req.session[managerId]&&req.session[managerId].day==new Date().toLocaleDateString()){
                                                req.session[managerId]={day:new Date().toLocaleDateString(),times:2};
                                            }else{
                                                req.session[managerId]={day:new Date().toLocaleDateString(),times:1};
                                            }

                                            // console.log(req.session[managerId]);
                                            res.json({"status":1,"msg":"你的提现人民币"+money+"元的请求已经发出！请留意你的微信转账记录！"})

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
}
