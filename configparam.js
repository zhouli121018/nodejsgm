module.exports = {
    //gameId,redCard显示隐藏
    host:'120.78.130.91',
    searchRoomUrl:'http://juzi.qhlongqing.com:8078/NN/getNum?type=all',
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