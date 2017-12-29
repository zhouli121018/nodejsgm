/**
 * Created by Administrator on 2017-12-29.
 */
var captchapng = require('captchapng');
const qs=require('querystring');

module.exports = {
    getCode:(req,res)=>{
        var code = '0123456789';
        var length = 4;
        var randomcode = '';
        for (var i = 0; i < length; i++) {
            randomcode += code[parseInt(Math.random() * 1000) % code.length];
        }
        req.session.code=randomcode;
        console.log('验证码：'+req.session.code);
        // 输出图片
        var p = new captchapng(300,50,parseInt(randomcode)); // width,height,numeric captcha
        p.color(255, 255, 255, 0);  // First color: background (red, green, blue, alpha)
        p.color(80, 80, 80, 150); // Second color: paint (red, green, blue, alpha)
        var img = p.getBase64();
        var imgbase64 = new Buffer(img,'base64');
        res.writeHead(200, {
            'Content-Type': 'image/png'
        });
        res.end(imgbase64);
    }


}
