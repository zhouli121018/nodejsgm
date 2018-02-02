/**
 * Created by Administrator on 2017-12-29.
 */
const mysql = require('mysql');
const config=require('./configparam.js');

module.exports=mysql.createPool({
    host:config.host,//qingyuankx 183.131.200.109 // 朝阳 47.95.239.253 //juyou 116.62.56.47 //ningdu 120.77.43.40//qingyuan120.76.100.224 //suzhou 121.196.221.247// songyuan 39.106.132.18 // qingyuan1213 103.73.206.31 //测试 120.79.23.45 //桔子 120.78.130.91
    //user:'root',//mahjong
    //password:'123456',//a257joker
    user:'mahjong',
    password:'a257joker',//a257joker!@#Q
    database:'mahjong_hbe',//mahjong_cy mahjong_hbe
    // connectionLimit:10
});