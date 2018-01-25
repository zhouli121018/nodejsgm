module.exports = {
    //gameId,redCard显示隐藏
    host:'47.95.239.253',//qingyuankx 183.131.200.109 // 朝阳 47.95.239.253 //juyou 116.62.56.47 //ningdu 120.77.43.40//qingyuan120.76.100.224 //suzhou 121.196.221.247// songyuan 39.106.132.18 // qingyuan1213 103.73.206.31 //测试 120.79.23.45 //桔子 120.78.130.91
    database:'mahjong_cy',//mahjong_cy mahjong_hbe
    searchRoomUrl:'http://47.95.239.253:8079/qymj/getNum?type=all',//朝阳http://47.95.239.253:8079/qymj/getNum?type=all,//清远http://kx.waleqp.com:8079/qymj/getNum?type=all //桔子棋牌http://juzi.qhlongqing.com:8078/NN/getNum?type=all
    wxappid:'wx3b8f3128e3557e48',
    mch_id:"1495156032",
    wxpaykey:"LQ5io7xwboFxx76523uIArDFiqlyaWwi",
    getRebate:(powerId)=>{
        var rebate=0;
        if(powerId==5){
            rebate="0.7";
        }else if(powerId==4){
            rebate="0.6";
        }else if(powerId==3){
            rebate="0.5";
        }else if(powerId==2){
            rebate="0.4";
        }
        console.log("configrebate:"+rebate);
        return rebate;
    }
}