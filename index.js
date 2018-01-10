/**
 * Created by 51216 on 2017/11/22.
 */
var url = require('url');
const http=require('http');
const express=require('express');
const code = require('./code');
const cash = require('./cash');
const myVip = require('./myVip');
const myAgent = require('./myAgent');
const detail = require('./detail');
const note = require('./note');
const notice = require('./notice');

var cookieParser = require('cookie-parser');
var session = require('express-session');

process.on('uncaughtException', function (err) {
   //打印出错误
   console.log(err);
   //打印出错误的调用栈方便调试
   console.log(err.stack);
});

var app=express();
var server=http.createServer(app);
server.listen(9081);
app.use(express.static('./public'));
app.use(cookieParser('sessiontest'));

app.use(session({
    secret: 'sessiontest',//与cookieParser中的一致
    resave: true,
    saveUninitialized:true,
    cookie:{
        maxAge: 1000*60*30 // default session expiration is set to 1 hour
    }
}));
app.use(function(req, res, next){
    var url = req.path;
    //console.log(url);
    if(req.session.user){
        req.session._garbage = Date();
        req.session.touch();
        next();
    }else if(url=='/login'||url=='/getCode'||url=='/logout'){
        next();
    }else{
        res.json({"timeout":1});
    }
});
//获取验证码
app.get('/getCode',code.getCode);
//登录
app.get('/login',myAgent.login);
//退出登录
app.get('/logout',(req,res)=>{
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

//获取当前在线人数等信息
app.get('/getRoomNumber',detail.getRoomNumber);
//获取代理信息
app.get('/getAgentInfo',myAgent.getAgentInfo);
//查询我的代理
app.get('/getMyAgents',myAgent.getMyAgents);
//查询子级代理
app.get('/getChildAgents',myAgent.getChildAgents);
//获取levelStr
app.get('/getlevelStr',myAgent.getlevelStr);
//修改密码/resetPassword
app.post('/resetPassword',myAgent.resetPassword);
//验证邀请码
app.get('/validInviteCode',myAgent.validInviteCode);
//新增代理验证邀请码addValidInviteCode
app.get('/addValidInviteCode',myAgent.addValidInviteCode);
//验证游戏ID
app.get('/validUuid',myAgent.validUuid);
//新增代理验证游戏ID addValidUuid
app.get('/addValidUuid',myAgent.addValidUuid);
//获取我的会员
app.get('/getAccount',myVip.getAccount);
//重新绑定上级代理邀请码 验证uuidvalidInviteCodeReManagerUpId
app.get('/validUuidReManagerUpId',myVip.validUuidReManagerUpId);
//重新绑定上级代理邀请码 验证invitecode
app.get('/validInviteCodeReManagerUpId',myVip.validInviteCodeReManagerUpId);
//重新绑定上级代理邀请码
app.get('/reManagerUpId',myVip.reManagerUpId);
//玩家充值验证游戏ID vipChargeValidUuid
app.get('/vipChargeValidUuid',myVip.vipChargeValidUuid);
//修改代理信息
app.post('/updateManagerInfo',myAgent.updateManagerInfo);
//代理充值
app.post('/updateAccount',myAgent.updateAccount);
//玩家充值
app.post('/vipCharge',myVip.vipCharge);
//验证上级代理邀请码
app.get('/validParentInviteCode',myAgent.validParentInviteCode);
//新增代理信息
app.post('/insertManager',myAgent.insertManager);
//修改玩家账号状态
app.get('/changeAccountStatus',myVip.changeAccountStatus);
//获取提现流水
app.get('/getNotes',note.getNotes);
//获取下级用户数量
app.get('/getVipCount',myAgent.getVipCount);
//获取下级代理数量
app.get('/getAgentCount',myAgent.getAgentCount);
//获取下级用户充值金额，计算收益
app.get('/getmineone',myAgent.getmineone);
//获取下级代理用户充值金额，计算收益
app.get('/getminetwo',myAgent.getminetwo);
//获取一周内每天新增会员数量
app.get('/getAddVipCount/day',myVip.getAddVipCountDay);
//获取近六周新增会员数量
app.get('/getAddVipCount/week',myVip.getAddVipCountWeek);
//获取半年内每月新增会员数量
app.get('/getAddVipCount/month',myVip.getAddVipCountMonth);
//获取账单明细
app.get('/getPaylogs',detail.getPaylogs);
//获取一周内每天充值总金额
app.get('/getTotalMoney/day',detail.getTotalMoneyDay);
//获取近六周每周充值总金额
app.get('/getTotalMoney/week',detail.getTotalMoneyWeek);
//获取半年内每月充值总金额
app.get('/getTotalMoney/month',detail.getTotalMoneyMonth);
//获取代理上次提现剩余的收益
app.get('/getRemain',myAgent.getRemain);
//代理提现
app.post('/tixian',cash.tixian);
//获取全部公告
app.get('/getAllNotice',notice.getAllNotice);
//新增公告
app.get('/addNotice',notice.addNotice);
//修改公告信息
app.get('/editNotice',notice.editNotice);
//获取我的代理数据
app.get('/getManagers',myAgent.getManagers);
//删除代理
app.get('/deleteManager',myAgent.deleteManager);
//重新绑定上级代理验证代理id
app.get('/validManagerId',myAgent.validManagerId);
//重新绑定上级代理
app.get('/reupCode',myAgent.reupCode);
