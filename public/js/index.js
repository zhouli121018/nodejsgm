/**
 * Created by 51216 on 2017/11/22.
 */
$('#tablist li a').click(function(e){
    if ( e && e.preventDefault )
        e.preventDefault();
    else
        window.event.returnValue = false;
    var id=$(this).attr('href');
    console.log(id);
    $(this).parent().addClass('active').siblings().removeClass('active');
    $(id).show().siblings().hide();
})
$(function(){
    $.ajax({
        url:'/getAgentInfo',
        data:{managerId:15},
        success:function(data){
            console.log(data);
            var html='';
            html=`
                <tr>
                    <td>姓名：</td>
                    <td>${data.name}</td>
                </tr>
                <tr>
                    <td>游戏ID：</td>
                    <td>${data.uuid}</td>
                </tr>
                <tr>
                    <td>游戏昵称：</td>
                    <td>${data.nickName}</td>
                </tr>
                <tr>
                    <td>代理编码：</td>
                    <td>${data.id}</td>
                </tr>
                <tr>
                    <td>邀请码：</td>
                    <td>${data.inviteCode}</td>
                </tr>
                <tr>
                    <td>手机号：</td>
                    <td>${data.telephone}</td>
                </tr>
                <tr>
                    <td>微信：</td>
                    <td>${data.weixin}</td>
                </tr>
                <tr>
                    <td>QQ：</td>
                    <td>${data.qq}</td>
                </tr>
                <tr>
                    <td>代理级别：</td>
                    <td>${data.power_id==5?'皇冠代理':(data.power_id==4?'钻石代理':(data.power_id==3?'铂金代理':(data.power_id==2?'黄金代理':'系统管理员')))}</td>
                </tr>
                <tr>
                    <td>分成比例：</td>
                    <td>${data.rebate}</td>
                </tr>
            `;
            $('#info table#infoTbl tbody').html(html);
            $('#info table#infoTbl td').each(function(i,dom){
                if($(this).html()=='null'){
                    $(this).html('');
                }
            })
        }
    });
    $.ajax({
        url:'/getManagers',
        data:{managerId:15},
        success:function(data){
            console.dir(data);
        }
    })

})