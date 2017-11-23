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
});

$(function(){
    if(sessionStorage['loginInviteCode']){
        $('#login').hide().siblings().show();
        console.log(1);
    }else{
        $('#login').show().siblings().hide();
        console.log(2);
    }
    $('#loginBtn').click(function(){
        if($('#uname').val()==''||$('#pwd').val()==''){
            alert('用户名或密码不能为空！');
            return;
        }
        var str=$('#loginForm').serialize();
        console.log(str);
        var md5pwd=$.md5($('#pwd'));
        cosole.log(md5pwd);
        $.ajax({
            url:'/login',
            data:{uname:$('#uname').val(),pwd:md5pwd},
            success:function(data){
                console.log(data);
            }
        })
    })

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
                    <td>剩余蓝钻：</td>
                    <td>${data.roomCard}</td>
                </tr>
                <tr>
                    <td>剩余红钻：</td>
                    <td>${data.redCard}</td>
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
            for(var i=0,html='';i<data.length;i++){
                var o=data[i];
                html+=`
                <tr>
                    <td>${o.id}</td>
                    <td>${o.uuid}</td>
                    <td>${o.nickName}</td>
                    <td>${o.power_id==5?'皇冠代理':(o.power_id==4?'钻石代理':(o.power_id==3?'铂金代理':(o.power_id==2?'黄金代理':'系统管理员')))}</td>
                    <td>${o.name}</td>
                    <td>${o.telephone}</td>
                    <td>${o.inviteCode}</td>
                    <td>${o.accountNumber}</td>
                    <td>${o.agentNumber}</td>
                    <td>${o.sumMoney}</td>
                    <td>${o.status==0?'正常':'禁用'}</td>
                    <td>
                    <button type="button" class="btn btn-default btn-sm" data-id="${o.id}">晋升</button>
                    <button class="btn btn-primary btn-sm" type="button" data-id="${o.id}">禁用</button></td>
                </tr>
                `;
            }
            $('#agent #agentTbl tbody').html(html);
        }
    });
    $.ajax({
        url:'/getAccounts',
        data:{managerId:15},
        success:function(data){
            console.dir(data);
            for(var i=0,html='';i<data.length;i++){
                var o=data[i];
                html+=`
                <tr>
                    <td>${o.uuid}</td>
                    <td>${o.nickName}</td>
                    <td>${o.roomCard}</td>
                    <td>${o.redCard}</td>
                    <td>${o.status==0?'正常':'禁用'}</td>
                    <td>${o.createTime}</td>
                    <td>
                    <button type="button" class="btn btn-default btn-sm" data-id="${o.uuid}">标记红名</button>
                    <button class="btn btn-primary btn-sm" type="button" data-id="${o.uuid}">禁用</button></td>
                </tr>
                `;
            }
            $('#vip #vipTbl tbody').html(html);
        }
    });

    $.ajax({
        url:'/getDetails',
        data:{managerId:15},
        success:function(data){
            console.dir(data);
            for(var i=0,html='';i<data.length;i++){
                var o=data[i];
                html+=`
                <tr>
                    <td>${o.muuid}</td>
                    <td>${o.inviteCode}</td>
                    <td>${o.name}</td>
                    <td>${o.power_id==5?'皇冠代理':(o.power_id==4?'钻石代理':(o.power_id==3?'铂金代理':(o.power_id==2?'黄金代理':'系统管理员')))}</td>
                    <td>${(o.money*o.rebate).toFixed(2)}</td>
                    <td>${o.payTime}</td>
                    <td>${(o.payType==0&&o.status==1)?o.uuid:''}</td>
                    <td>${(o.payType==0&&o.status==1)?o.nickName:''}</td>
                    <td>${(o.payType==0&&o.status==1)?o.money:''}</td>
                    <td>${(o.payType==0&&o.status==1)?o.money*o.rebate:''}</td>
                    <td>${o.payType==0?'分成':'提现'}</td>
                </tr>
                `;
            }
            $('#detail #detailTbl tbody').html(html);
        }
    })
});