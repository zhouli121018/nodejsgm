/**
 * Created by 51216 on 2017/11/22.
 */


$(function(){
    Date.prototype.Format = function (fmt) {
        var o = {
            "M+": this.getMonth() + 1, //月份
            "d+": this.getDate(), //日
            "H+": this.getHours(), //小时
            "m+": this.getMinutes(), //分
            "s+": this.getSeconds(), //秒
            "q+": Math.floor((this.getMonth() + 3) / 3), //季度
            "S": this.getMilliseconds() //毫秒
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o)
            if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    };
    if(sessionStorage['loginInviteCode']){
        console.log(1);
    }else{
        location.href="index.html";
    }

    var now=new Date();
    var begin=new Date();
    // begin.setDate(begin.getDate());
    now.setDate(now.getDate()+1);

    var overArr=now.toLocaleDateString().split('/');
    for(var i=0;i<overArr.length;i++){
        if(overArr[i]<10){
            overArr[i]=0+overArr[i];
        }
    }
    var overTime=overArr.join('-');
    var beginArr=begin.toLocaleDateString().split('/');
    for(var i=0;i<beginArr.length;i++){
        if(beginArr[i]<10){
            beginArr[i]=0+beginArr[i];
        }
    }
    var beginTime=beginArr.join('-');
    $('[name=endtime]').val(overTime);
    $('[name=starttime]').val(beginTime);


    function refresh(){
        console.log('refresh');
        $.ajax({
            url:'/refresh',
            success:function(data){
                console.log(data);
                if(data.status>0){
                    console.log(11211);
                    getAgentInfo();
                }else{
                    console.log(11211211);
                    sessionStorage.clear();
                    location.href="index.html";
                }
            }
        });
        var paths=window.location.href;
        // alert(paths);
        var path=paths.slice(paths.indexOf('#'));
        // alert(path);
        $('#tablist li').removeClass('active');
        $('#tablist li a').each(function(i,dom){
            if($(dom).attr('href')==path){
                $(dom).parent().addClass('active');

            }
        })
        $(path).show().siblings().hide();
        var id=path;
        if(id=="#agent"){
            getMyAgents(1);
        }else if(id=="#vip"){
            getAccount(1);
        }else if(id=="#detail"){
            getPaylogs(1);
        }else if(id=="#info"){
            getAgentInfo();
        }else if(id=="#note"){
            getNotes(1);
        }else if(id=="#notice"){
            getNotice();
        }else{
            $('#tablist li a[href=#info]').parent().addClass('active').siblings().removeClass('active');
            getAgentInfo();
        }

    }
    refresh();

    function getRoom(){
        $.ajax({
            url:'/getRoomNumber',
            success:function(data){
                console.log('dangqianrenshu');
                console.log(data);
                var dataArr=data.split(/\s+/);
                for(var i=0,html='';i<dataArr.length;i++){
                    html+=`
                <li><b>${dataArr[i]}</b></li>
                `;
                }
                $('#nowInfo').html(html);
            }
        })
    }
    $('#tablist li a').click(function(e){
        // if ( e && e.preventDefault )
        //     e.preventDefault();
        // else
        //     window.event.returnValue = false;
        var id=$(this).attr('href');
        if(id=="#agent"){
            getMyAgents(1);
        }else if(id=="#vip"){
            getAccount(1);
        }else if(id=="#detail"){
            getPaylogs(1);
        }else if(id=="#info"){
            getAgentInfo();
        }else if(id=="#note"){
            getNotes(1);
        }else if(id=="#notice"){
            getNotice();
        }
        console.log(id);
        $(this).parent().addClass('active').siblings().removeClass('active');
        $(id).show().siblings().hide();

    });

    function logout(){
        $.ajax({
            url:'/logout',
            success:function(data){
                console.log(data);
            }
        });
        sessionStorage.clear();
        location.href='index.html';
    }
    $('#logout').click(function(){
        logout();
    });
    function getAgentInfo(){
        $.ajax({
            url:'/getAgentInfo',
            async: false,
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
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
                <tr>
                    <td>下级代理数量：</td>
                    <td id="agentCount"></td>
                </tr>
                <tr>
                    <td>下级会员数量：</td>
                    <td id="vipCount"></td>
                </tr>
                <tr>
                    <td>上次登录时间：</td>
                    <td>${data.lastLoginTime?new Date(data.lastLoginTime).Format("yyyy-MM-dd HH:mm:ss"):'---'}</td>
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
            url:'/getVipCount',
            success:function(data){
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                console.log("vipcount:");
                console.log(data);
                $("#vipCount").html(data.vipCount);
            }
        })
        $.ajax({
            url:'/getAgentCount',
            success:function(data){
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                $("#agentCount").html(data.agentCount);
            }
        });
        if(sessionStorage['powerId']>1){
            var total=0;
            $.ajax({
                url:'/getmineone',
                async: false,
                success:function(data){
                    console.log(123456789);
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    console.log(data);
                    $('#mineone').html(data.mineone.toFixed(2));
                    total+=parseFloat(data.mineone.toFixed(2));
                    console.log(total);
                }
            });
            $.ajax({
                url:'/getminetwo',
                async: false,
                success:function(data){
                    console.log("minetwo");
                    console.log(data);
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    $('#minetwo').html(data.minetwo.toFixed(2));
                    total+=parseFloat(data.minetwo.toFixed(2));
                    console.log(total);
                }
            });
            $.ajax({
                url:'/getRemain',
                async: false,
                success:function(data){
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    console.log("getRemain");
                    console.log(data);
                    var remain=0.00;
                    if(data.length>0){
                        remain=data[0].money.toFixed(2);
                    }
                    console.log(remain);
                    $('#remain').html(remain);
                    total+=parseFloat(remain);
                    console.log(total);
                }
            });
            $('#total-bonus').html(total.toFixed(2));
        }


    }
    function getMyAgents(page){
        var starttime=$("#searchAgentForm [name=starttime]").val();
        var endtime=$("#searchAgentForm [name=endtime]").val();
        var managerId=$("#searchAgentForm [name=managerId]").val();
        var uname=$("#searchAgentForm [name=uname]").val();
        var invitecode=$("#searchAgentForm [name=invitecode]").val();
        var powerId=$("#searchAgentForm [name=powerId]").val();
        var gameId=$("#searchAgentForm [name=gameId]").val();
        if(powerId==0){powerId=''};
        if(gameId==0){gameId=''};
        $.ajax({
            url:'/getMyAgents',
            data:{starttime:starttime,endtime:endtime,page:page,managerId:managerId,uname:uname,invitecode:invitecode,powerId:powerId,gameId:gameId},
            success:function(datas){
                if(datas.timeout==1){
                    location.href="index.html";
                    return;
                }
                var data=datas.managers;
                var totalNum=datas.totalNum;
                var totalMoney=datas.totalMoney;
                $('#agent .total-number').html(totalNum);
                $('#agent .total-money').html(totalMoney);
                if(data.length>0){
                    for(var i=0,html='';i<data.length;i++){
                        var o=data[i];
                        html+=`
                        <tr>
                            <td>${o.id}</td>
                            <td>${o.name}</td>
                            <td>${o.uuid||''}</td>
                            <td>${o.nickName||''}</td>
                            <td data-powerId="${o.power_id}">${o.power_id==5?'皇冠代理':(o.power_id==4?'钻石代理':(o.power_id==3?'铂金代理':(o.power_id==2?'黄金代理':'系统管理员')))}</td>
                            <td>${o.rebate}</td>
                            <td>${o.telephone}</td>
                            <td>${o.inviteCode}</td>
                            <td>${o.roomCard||0}</td>
                            <td>${o.bmount||0}</td>
                            <td>${o.userCounts}</td>
                            <td>${o.agentNum}</td>
                            <td>${o.totalMoney}</td>
                            <td data-status="${o.status}">${o.status==0?'正常':'禁用'}</td>
                            <td>${o.manager_up_id}</td>
                            <td>${o.lastLoginTime?new Date(o.lastLoginTime).Format("yyyy-MM-dd HH:mm:ss"):'---'}</td>
                            <td>
                            <button type="button" class="btn btn-warning btn-sm editAgent" data-id="${o.id}">编辑</button>
                            <button class="btn btn-success btn-sm chargeForAgent" type="button" data-id="${o.id}">充值</button></td>
                        </tr>
                    `
                    }
                    $('#agentTbl tbody').html(html);
                    var totalpages=1;
                    if(totalNum%10==0){
                        totalpages=totalNum/10;
                    }else{
                        totalpages=totalNum/10+1;
                    }
                    var options = {
                        currentPage: page,
                        totalPages:totalpages,
                        bootstrapMajorVersion: 3,
                        onPageChanged: function(e,oldPage,newPage){
                            getMyAgents(newPage);
                        }
                    };

                    $('#agent-pages').bootstrapPaginator(options);
                }else{
                    $('#agentTbl tbody').html('');
                    $('#agent-pages').html('');
                }


            }
        })
    }
    function getPaylogs(indexPage){
        getRoom();
        var starttime=$("#searchDetailForm [name=starttime]").val();
        var endtime=$("#searchDetailForm [name=endtime]").val();
        var uuid=$("#searchDetailForm [name=uuid]").val();
        var managerId=$("#searchDetailForm [name=managerId]").val();
        var gameId=$("#searchDetailForm [name=gameId]").val();
        if(gameId==0){gameId=''};
        var plevelStr='';
        if(managerId){
            $.ajax({
                url:'/getlevelStr',
                async: false,
                data:{managerId:managerId},
                success:function(data){
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    console.log('levelstr');
                    console.log(data);
                    plevelStr=data[0].levelStr;
                }
            })
        }
        $.ajax({
            url:'/getPaylogs',
            data:{page:indexPage,starttime:starttime,endtime:endtime,uuid:uuid,managerId:managerId,plevelStr:plevelStr,gameId:gameId},
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                var paylogs=data.paylogs;
                var totalBonus=data.totalBonus;
                var totalNum=data.totalNum;
                var totalMoney=data.totalMoney;

                $('#totalBonus b').html(totalBonus);
                $('#detail .total-number').html(totalNum);
                $('#detail .total-money').html(totalMoney);
                if(paylogs.length>0){
                    for(var i=0,html='';i<paylogs.length;i++){
                        var o=paylogs[i];
                        html+=`
                <tr>
                    <td>${o.managerId}</td>
                    <td>${o.name}</td>
                    <td>${o.uuid}</td>
                    <td>${o.nickName}</td>
                    <td>${o.money}</td>
                    <td>${new Date(o.payTime).Format("yyyy-MM-dd HH:mm:ss")}</td>
                    <td>${o.bonus||'---'}</td>
                    <td>${o.gameId}</td>
                </tr>
                `
                    }
                    $('#detailTbl tbody').html(html);

                    var totalpages=1;
                    if(totalNum%10==0){
                        totalpages=totalNum/10;
                    }else{
                        totalpages=totalNum/10+1;
                    }
                    var options = {
                        currentPage: indexPage,
                        totalPages:totalpages,
                        bootstrapMajorVersion: 3,
                        onPageChanged: function(e,oldPage,newPage){
                            getPaylogs(newPage);
                        }
                    };

                    $('#detail-pages').bootstrapPaginator(options);
                }else{
                    $('#detailTbl tbody').html('');
                    $('#detail-pages').html('');
                }

            }
        });

        fusionDetail('day','每日','column2d');
    }
    function getNotes(page){
        var starttime=$("#searchNoteForm [name=starttime]").val();
        var endtime=$("#searchNoteForm [name=endtime]").val();
        var managerId=$("#searchNoteForm [name=managerId]").val();
        $.ajax({
            url:'/getNotes',
            data:{starttime:starttime,endtime:endtime,page:page,managerId:managerId},
            success:function(datas){
                if(datas.timeout==1){
                    location.href="index.html";
                    return;
                }
                var data=datas.notes;
                var totalNum=datas.totalNum;
                var totalMoney=datas.totalMoney;
                $('#note .total-number').html(totalNum);
                $('#note .total-money').html(totalMoney);
                if(data.length>0){
                    for(var i=0,html='';i<data.length;i++){
                        var o=data[i];
                        html+=`
                        <tr>
                            <td>${o.managerId||o.id}</td>
                            <td>${o.name}</td>
                            <td>${o.inviteCode||''}</td>
                            <td>${o.money}</td>
                            <td>${o.payTime?new Date(o.payTime).Format("yyyy-MM-dd HH:mm:ss"):'----'}</td>
                            <!--<td>${o.status==1?'已完成':'提现失败'}</td>-->
                        </tr>
                    `
                    }
                    $('#noteTbl tbody').html(html);
                    var totalpages=1;
                    if(totalNum%10==0){
                        totalpages=totalNum/10;
                    }else{
                        totalpages=totalNum/10+1;
                    }
                    var options = {
                        currentPage: page,
                        totalPages:totalpages,
                        bootstrapMajorVersion: 3,
                        onPageChanged: function(e,oldPage,newPage){
                            getNotes(newPage);
                        }
                    };

                    $('#note-pages').bootstrapPaginator(options);
                }else{
                    $('#noteTbl tbody').html('');
                    $('#note-pages').html('');
                }


            }
        })
    }
    function getAccount(page){
        var starttime=$("#searchVipForm [name=starttime]").val();
        var endtime=$("#searchVipForm [name=endtime]").val();
        var managerId=$("#searchVipForm [name=managerId]").val();
        var uuid=$("#searchVipForm [name=uuid]").val();
        $.ajax({
            url:'/getAccount',
            data:{starttime:starttime,managerId:managerId,endtime:endtime,uuid:uuid,page:page},
            success:function(datas){
                console.dir(datas);
                if(datas.timeout==1){
                    location.href="index.html";
                    return;
                }
                var data=datas.accounts;
                var totalNum=datas.totalNum;
                if(data&&data.length>0){
                    for(var i=0,html='';i<data.length;i++){
                        var o=data[i];
                        var redCardStr=0;
                        if(o.redCard){
                            redCardStr=o.redCard;
                        }
                        var editStr='';
                        if(o.status==0){
                            editStr=`<option value="1">标记红名</option><option value="2">禁用</option>`;
                        }else if(o.status==1) {
                            editStr=`<option value="0">取消红名</option><option value="2">禁用</option>`;
                        }else if(o.status==2) {
                            editStr=`<option value="0">启用</option>`;
                        }

                        html+=`
                        <tr>
                            <td>${o.Uuid||o.uuid}</td>
                            <td>${o.nickName}</td>
                            <td>${o.manager_up_id}</td>
                            <td>${o.totalMoney}</td>
                            <td>${o.roomCard}</td>
                            <td>${redCardStr}</td>
                            <td><b>${o.status==0?'正常':'禁用'}</b></td>
                            <td>${new Date(o.createTime).Format("yyyy-MM-dd HH:mm:ss")}</td>
                            <td>
                                <span class="input-group editStatus">
                                <select class="form-control">${editStr}</select>
                                <button data-id="${o.uuid}" class="btn btn-warning updateStatus">确定</button>
                                </span>
                            </td>
                        </tr>
                        `;
                    }
                    $('#vip #vipTbl tbody').html(html);
                    var totalpages=1;
                    if(totalNum%10==0){
                        totalpages=parseInt(totalNum/10);
                    }else{
                        totalpages=parseInt(totalNum/10)+1;
                    }
                    var options = {
                        currentPage: page,
                        totalPages:totalpages,
                        bootstrapMajorVersion: 3,
                        onPageChanged: function(e,oldPage,newPage){
                            getAccount(newPage);
                        }
                    };
                    $('#vip-pages').bootstrapPaginator(options);
                    $('#vip .total-number').html(totalNum);
                }else{
                    $('#vip-pages').html('');
                    $('#vip .total-number').html(0);
                    $('#vip #vipTbl tbody').html('');
                }

            }
        });

        rendFusionCharts('day','每日','column2d');
    }
    $('#vip').on('click','.updateStatus',function(){
        var uuid=$(this).attr('data-id');
        var status=$(this).prev().val();
        if(confirm('确定修改账号ID' +uuid+ '状态吗？')){
            $.ajax({
                url:'/changeAccountStatus',
                data:{uuid:uuid,status:status},
                success:function(data){
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    console.log(data);
                    if(data>0){
                        alert('修改成功！');
                    }else{
                        alert('修改失败！');
                    }
                    var page=parseInt($('#vip-pages li.active a').html());
                    getAccount(page);
                }
            })
        }

    })
    //getAgentInfo();
    function resetPassword(){
        var str1=prompt('请输入新密码：');
        if(str1==null){
            return;
        }
        var str2=prompt('请再次输入新密码：');
        if(str1!=str2){
            alert('两次输入密码不一致！请重新输入！');
            return;
        }else if((str1!=null)&&str1==str2&&confirm("确定修改密码？")){

            $.ajax({
                type: "POST",
                url:"/resetPassword",
                data: {newPwd:hex_md5(str1)},
                success: function data(data){
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    console.log(data);
                    if(data.status==1)
                        alert('修改密码成功！');
                    else
                        alert('修改密码失败!');
                }
            });

        }
    }
    $('#resetPwd').click(function(){
        resetPassword();
    });
    function getChildAgents(id,ele,level){

        console.log(id);
        $.ajax({
            url:'/getChildAgents',
            data:{managerId:id},
            success:function(data){
                console.dir(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                for(var i=0,html='';i<data.length;i++){
                    var o=data[i];
                    if(o.agentNumber>0){
                        html+=`
                <tr data-parent="${id}">
                    <td data-level="${level}" class="childAgent ${"level"+level}"><span class="tree-collapse"></span><b>${o.id}</b></td>`
                    }else{
                        html+=`
                <tr data-parent="${id}">
                    <td data-level="${level}" class="${"level"+level}"><span></span><b>${o.id}</b></td>`
                    }

                    html+=`
                    <td>${o.name}</td>
                    <td>${o.uuid}</td>
                    <td>${o.nickName}</td>
                    <td data-powerId="${o.power_id}">${o.power_id==5?'皇冠代理':(o.power_id==4?'钻石代理':(o.power_id==3?'铂金代理':(o.power_id==2?'黄金代理':'系统管理员')))}</td>
                    <td>${o.rebate}</td>
                    <td>${o.telephone}</td>
                    <td>${o.inviteCode}</td>
                    <td>${o.roomCard}</td>
                    <td>${o.redCard}</td>
                    <td>${o.accountNumber}</td>
                    <td>${o.agentNumber}</td>
                    <td>${o.sumMoney}</td>
                    <td data-status="${o.status}">${o.status==0?'正常':'禁用'}</td>
                    <td>
                    <button type="button" class="btn btn-warning btn-sm editAgent" data-id="${o.id}">编辑</button>
                    <button class="btn btn-success btn-sm chargeForAgent" type="button" data-id="${o.id}">充值</button></td>
                </tr>
                `;
                }
                ele.after(html);
            }
        })
    }
    $("#agent #agentTbl tbody").on("click",'td span.tree-collapse',function(){
        var mid=$(this).next().html();
        var ele=$(this).parents('tr');
        $(this).removeClass('tree-collapse').addClass('tree-expend');
        var level=parseInt($(this).parents('td').attr('data-level'))+1;
        if(sessionStorage['powerId']==1){
            getChildAgents(mid,ele,level);
        }
    });
    $("#agent #agentTbl tbody").on("click",'td span.tree-expend',function(){
        var mid=$(this).next().html();
        $(this).removeClass('tree-expend').addClass('tree-collapse');
        $("#agentTbl [data-parent='"+mid+"']").hide();
    })

    $('#agent #agentTbl').on('click','.editAgent',function(){
        var mid=$(this).attr('data-id');
        var nowTr=$(this).parents('tr');
        $('#agent #agentDetail .uname').val(nowTr.find('td:eq(1)').html());
        $("#agent #agentDetail [name='mid']").val(mid);
        $("#agent #agentDetail [name='uuid']").val(nowTr.find('td:eq(2)').html());
        $("#agent #agentDetail [name='rebate']").val(nowTr.find('td:eq(5)').html());
        $("#agent #agentDetail [name='telephone']").val(nowTr.find('td:eq(6)').html());
        $("#agent #agentDetail [name='inviteCode']").val(nowTr.find('td:eq(7)').html());
        $("#agent #agentDetail [name='powerId']").val(nowTr.find('td:eq(4)').attr('data-powerId'));
        $("#agent #agentDetail [name='status']").val(nowTr.find('td:eq(13)').attr('data-status'));
        $('#agent #agentDetail').fadeIn();
    });
    $('#agent #agentDetail .sure').click(function(){
        var str=$('#agentDetailForm').serialize();
        console.log(str);
        var mid=$("#agent #agentDetail [name='mid']").val();
        var inputInviteCode=$("#agent #agentDetail [name='inviteCode']").val();
        var telephone=$("#agent #agentDetail [name='telephone']").val();
        var rebate=$("#agent #agentDetail [name='rebate']").val();
        var powerId=$("#agent #agentDetail [name='powerId']").val();
        var validInviteCode=false;
        var validUuid=false;
        if(inputInviteCode==''){
            alert('邀请码不能为空！请输入邀请码！');
            return;
        }
        var rebetreg=/^0\.\d{1,2}$/;
        if(rebate!=""&& (!rebetreg.test(rebate))){
            $("#agent #agentDetail [name='rebate']").focus();
            alert('分成比例格式不正确！请重新输入！如：0.5 ');
            return;
        }
        if(rebate==''||rebate>=sessionStorage['rebate']){
            alert('请输入正确的分成比例！');
            return;
        }
        if(sessionStorage['powerId']!=1&&parseFloat(powerId)>=parseFloat(sessionStorage['powerId'])){
            alert('代理级别不能高于等于上级代理级别！请重新选择！');
            $("#agent #agentDetail [name='powerId']").focus();
            return;
        }
        $.ajax({
            url:'/validInviteCode',
            data:{managerId:mid,inviteCode:inputInviteCode},
            async: false,
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                if(data.length>0){
                    alert('该邀请码不可用！请重新输入！');
                    validInviteCode=false;
                    $("#agent #agentDetail [name='inviteCode']").focus();
                }else{
                    validInviteCode=true;
                }

            }
        });
        $.ajax({
            url:'/validUuid',
            async: false,
            data:str,
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                if(data.status==0){
                    alert('该游戏ID不存在或该游戏ID已设置为代理！');
                    $("#agent #agentDetail [name='uuid']").focus();
                    validUuid=false;
                }else if(data.status==1){
                    validUuid=true;
                }
            }
        });
        if(validInviteCode&&validUuid){
            $.ajax({
                url:'/updateManagerInfo',
                type:'POST',
                data:str,
                success:function(data){
                    console.log(data);
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    if(data.status==1){
                        alert('修改成功！');
                        $('#agent #agentDetail').hide();
                        var page=parseInt($('#agent-pages li.active a').html());
                        getMyAgents(page);
                    }
                }
            })
        }
    });

    $('#agent #agentTbl').on('click','.chargeForAgent',function(){
        var mid=$(this).attr('data-id');
        var nowTr=$(this).parents('tr');
        $("#agent #agentCharge [name='roomCardNum']").val('');
        $('#agent #agentCharge .uname').val(nowTr.find('td:eq(1)').html());
        $("#agent #agentCharge [name='uuid']").val(nowTr.find('td:eq(2)').html());
        $("#agent #agentCharge .roomCard").val(nowTr.find('td:eq(8)').html());
        $("#agent #agentCharge .redCard").val(nowTr.find('td:eq(9)').html());
        $('#agent #agentCharge').fadeIn();
    });
    $('#agent #agentCharge .sure').click(function(){
        var str=$('#agentChargeForm').serialize();
        console.log(str);
        var inputUuid=$("#agent #agentCharge [name='uuid']").val();
        var roomCardNum=$("#agent #agentCharge [name='roomCardNum']").val();
        if(roomCardNum!=''&&roomCardNum%1==0){
            if(sessionStorage['powerId']!=1&&roomCardNum<=0){
                alert('请输入正确的充钻数量！');
                return;
            }
        }else{
            alert('请输入正确的充钻数量！');
            return;
        }
        $.ajax({
            url:'/updateAccount',
            type:'POST',
            data:str,
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                if(data.status==1){
                    alert('充值成功！');
                    $('#agent #agentCharge').hide();
                    var page=parseInt($('#agent-pages li.active a').html());
                    getMyAgents(page);
                }else{
                    alert('充值失败！(请检查代理钻石数量是否足够)');
                }
            }
        })
    });

    $('#agent>button.add-agent').click(function(){
        $("#agent #add-message [name='parentInviteCode']").val(sessionStorage['loginInviteCode']);
        $('#agent #add-message').fadeIn();
    });
    $('#agent #add-message .sure').click(function(){
        var str=$('#addAgentForm').serialize();
        var pmid=sessionStorage['managerId'];
        var plevelStr='';
        var addRedCard=0;
        var validParentInviteCode=false;
        console.log(str);
        var validInviteCode=false;
        var validUuid=false;
        var inputInviteCode=$("#agent #add-message [name='inviteCode']").val();
        var inputUuid=$("#agent #add-message [name='uuid']").val();
        var uname=$("#agent #add-message [name='uname']").val();
        var telephone=$("#agent #add-message [name='telephone']").val();
        var weixin=$("#agent #add-message [name='weixin']").val();
        var rebate=$("#agent #add-message [name='rebate']").val();
        var powerId=$("#agent #add-message [name='powerId']").val();
        var nreg=/^([\u4e00-\u9fa5]){2,4}$/;
        var prebate=0;
        var ppowerId=0;
        if(!nreg.test(uname)){
            $("#agent #add-message [name='uname']").focus();
            alert('姓名格式不正确！请重新输入！');
            return;
        }
        var reg=/^1[34578]\d{9}$/;
        if(!reg.test(telephone)){
            $("#agent #add-message [name='telephone']").focus();
            alert('手机号码格式不正确！请重新输入！');
            return;
        }
        if(weixin==''){
            alert('微信号不能为空！请输入微信号！');
            $("#agent #add-message [name='weixin']").focus();
            return;
        }
        var rebetreg=/^0\.\d{1,2}$/;
        if(rebate!=""&& (!rebetreg.test(rebate))){
            $("#agent #add-message [name='rebate']").focus();
            alert('分成比例格式不正确！请重新输入！如：0.5 ');
            return;
        }
        if(inputInviteCode==''){
            alert('邀请码不能为空！请输入邀请码！');
            $("#agent #add-message [name='inviteCode']").focus();
            return;
        }
        $.ajax({
            url:'/addValidInviteCode',
            data:{inviteCode:inputInviteCode},
            async: false,
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                if(data.length>0){
                    alert('该邀请码不可用！请重新输入！');
                    validInviteCode=false;
                    $("#agent #add-message [name='inviteCode']").focus();
                }else{
                    validInviteCode=true;
                }
            }
        });
        $.ajax({
            url:'/addValidUuid',
            async: false,
            data:{uuid:inputUuid},
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                console.log(data.validuuid);
                if(data.validuuid==0){
                    alert('该游戏ID不存在或该游戏ID已设置为代理！');
                    $("#agent #add-message [name='uuid']").focus();
                    validUuid=false;
                }else {
                    console.log(data.redCard);
                    if(data.redCard){
                        addRedCard=data.redCard;
                    }
                    validUuid=true;
                }
            }
        });
        $.ajax({
            url:'/validParentInviteCode',
            async: false,
            data:{parentInviteCode:$("#agent #add-message [name='parentInviteCode']").val()},
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                if(data.length==0){
                    alert('上级代理邀请码不存在，请重新输入！');
                    validParentInviteCode=false;
                    $("#agent #add-message [name='parentInviteCode']").focus();
                }else{
                    console.log(data[0].id+"++++");
                    pmid=data[0].id;
                    plevelStr=data[0].levelStr||'';
                    prebate=data[0].rebate;
                    ppowerId=data[0].power_id;
                    validParentInviteCode=true;
                }
            }
        });
        if(ppowerId!=1&&parseFloat(powerId)>=parseFloat(ppowerId)){
            alert('代理级别不能高于等于上级代理级别！请重新选择！');
            $("#agent #add-message [name='powerId']").focus();
            return;
        }
        if(parseFloat(rebate)>=parseFloat(prebate)){
            alert('分成比例不能高于等于上级代理分成比例！请重新输入！');
            $("#agent #add-message [name='rebate']").focus();
            return;
        }
        if(validInviteCode&&validUuid&&validParentInviteCode){
            $.ajax({
                url:'/insertManager',
                data:str+"&pmid="+pmid+"&redCard="+addRedCard+"&plevelStr="+plevelStr,
                type:'POST',
                success:function(data){
                    console.log(data);
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    if(data.status==1){
                        alert('新增代理成功！');
                        $("#agent #add-message").hide();
                        getMyAgents(1);
                    }else{
                        alert('新增代理失败！')
                    }
                }
            })
        }

    })

    $('.close').click(function(){
        $(this).parent().parent().hide();
    });
    $('.cancel').click(function(){
        $(this).parents('form').parent().hide();
    });

    $('#searchAgent').click(function(){
        getMyAgents(1);
        //getManagers2();
    });

    $('#vip>button.charge').click(function(){
        $('#vip #vipCharge').fadeIn();
    });
    $('#vip #vipCharge .sure').click(function(){
        var uuid=$("#vipChargeForm [name='uuid']").val();
        var validUuid=false;
        $.ajax({
            url:'/vipChargeValidUuid',
            data:{uuid:uuid},
            async: false,
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                if(data.validuuid==0){
                    validUuid=false;
                    alert('此用户ID不存在或已禁用，请重新输入！');
                }else if(data.validuuid==1){
                    validUuid=true;
                }
            }
        });
        var roomCardNum=$("#vip #vipCharge [name='roomCardNum']").val();
        var redCardNum=$("#vip #vipCharge [name='redCardNum']").val();
        if(roomCardNum==''&&redCardNum==''){
            alert('请输入正确的充钻数量！');
            return;
        }
        if(roomCardNum.length!=0&&roomCardNum%1==0){
            if(sessionStorage['powerId']!=1&&roomCardNum<=0){
                alert('请输入正确的充钻数量！');
                return;
            }
        }
        if(redCardNum.length!=0&&redCardNum%1==0){
            if(sessionStorage['powerId']!=1&&redCardNum<=0){
                alert('请输入正确的充钻数量！');
                return;
            }
        }
        var str=$('#vipChargeForm').serialize();
        console.log(str);
        if(validUuid){
            $.ajax({
                url:'/vipCharge',
                data:str,
                type:'POST',
                success:function(data){
                    console.log(data);
                    if(data.timeout==1){
                        location.href="index.html";
                        return;
                    }
                    if(data.status==1){
                        $('#vipCharge').hide();
                        alert('充值成功！');
                        var page=parseInt($('#vip-pages li.active a').html());
                        getAccount(page);
                    }else{
                        alert('充值失败！(请检查代理钻石数量是否足够)');
                    }
                }
            })
        }
    });

    $('#vip #searchVip').click(function(){
        getAccount(1);
    })
    if(sessionStorage['powerId']==1){
        $('#totalBonus').hide();
        $('#info .info-hide').hide();
    }else{
        $('#detail .agentSearch').hide();
        $("#searchNoteForm .agentId").hide();
        $("#searchAgentForm .agentId").hide();
        $("#vip .redcard-hide").hide();
        $("#searchVipForm .agentId").hide();
        $('.fusion-charts>form .fusion-hide').hide();
        $('.detail-hide').hide();
        $('#tablist .powerId-hide').hide();
        $('#vip button.edit').hide();
    }
    $('#searchDetail').click(function(){
        getPaylogs(1);
    });
    $('#searchNote').click(function(){
        getNotes(1);
    })

    function rendFusionCharts(day,title,type,managerId){
        $.ajax({
            type: 'GET',
            data:{managerId:managerId},
            url: '/getAddVipCount/'+day,
            success: function(list){
                console.log(list);
                if(list.timeout==1){
                    location.href="index.html";
                    return;
                }
                //创建一个图表对象
                //var type=$(that).attr('href');
                //console.log(type);
                var c = new FusionCharts({
                    type: type,//'doughnut3d',//'doughnut2d',//'pie3d',//'pie2d',//'line',//'bar3d',//'bar2d',//'column3d',//'column2d',
                    renderAt: 'vipAddDay',
                    width: '100%',
                    height: 300,
                    dataSource: {
                        "chart": {
                            "caption": title+"新增会员数量",
                            //"subCaption": "一周",
                            //"xAxisName": "日期",
                            "yAxisName": "新增会员数量"
                            //Making the chart export enabled in various formats
                        },
                        data: list    //[{label:x, value:x}]
                    }
                });
                //渲染出来
                c.render();
            }
        });
    }


    $('.fusion-charts ul.nav-pills li a').click(function(e){
        if ( e && e.preventDefault )
            e.preventDefault();
        else
            window.event.returnValue = false;
        $(this).parent().addClass('active').siblings().removeClass('active');
        var type=$('#fusion-type').val();
        var day=$(this).attr('href');
        var title=$(this).attr('title');
        var managerId=$('#fusion-managerId').val();
        rendFusionCharts(day,title,type,managerId);
    })
    $('#fusion-search').click(function(){
        var managerId=$('#fusion-managerId').val();
        var day=$('.fusion-charts ul.nav-pills li.active a').attr('href');
        var title=$('.fusion-charts ul.nav-pills li.active a').attr('title');
        var type=$('#fusion-type').val();
        rendFusionCharts(day,title,type,managerId);
    })
    $('#type-sure').click(function(){
        var managerId=$('#fusion-managerId').val();
        var day=$('.fusion-charts ul.nav-pills li.active a').attr('href');
        var title=$('.fusion-charts ul.nav-pills li.active a').attr('title');
        var type=$('#fusion-type').val();
        rendFusionCharts(day,title,type,managerId);
    })


    function fusionDetail(day,title,type,managerId){
        $.ajax({
            type: 'GET',
            data:{managerId:managerId},
            url: '/getTotalMoney/'+day,
            success: function(list){
                console.log(list);
                if(list.timeout==1){
                    location.href="index.html";
                    return;
                }
                //创建一个图表对象
                //var type=$(that).attr('href');
                //console.log(type);
                var c = new FusionCharts({
                    type: type,//'doughnut3d',//'doughnut2d',//'pie3d',//'pie2d',//'line',//'bar3d',//'bar2d',//'column3d',//'column2d',
                    renderAt: 'fusionTotalMoney',
                    width: '100%',
                    height: 300,
                    dataSource: {
                        "chart": {
                            "caption": title+"充值金额",
                            //"subCaption": "一周",
                            //"xAxisName": "日期",
                            "yAxisName": "充值金额"
                            //Making the chart export enabled in various formats
                        },
                        data: list    //[{label:x, value:x}]
                    }
                });
                //渲染出来
                c.render();
            }
        });
    }
    $('#detail .fusion-charts ul.nav-pills li a').click(function(e){
        if ( e && e.preventDefault )
            e.preventDefault();
        else
            window.event.returnValue = false;
        $(this).parent().addClass('active').siblings().removeClass('active');
        var type=$('#fusion-detail-select').val();
        var day=$(this).attr('href');
        var title=$(this).attr('title');
        var managerId=$('#detail-managerId').val();
        fusionDetail(day,title,type,managerId);
    })
    $('#fusion-detail-search').click(function(){
        var managerId=$('#detail-managerId').val();
        var day=$('#detail .fusion-charts ul.nav-pills li.active a').attr('href');
        var title=$('#detail .fusion-charts ul.nav-pills li.active a').attr('title');
        var type=$('#fusion-detail-select').val();
        fusionDetail(day,title,type,managerId);
    })
    $('#fusion-detail-type').click(function(){
        var managerId=$('#detail-managerId').val();
        var day=$('#detail .fusion-charts ul.nav-pills li.active a').attr('href');
        var title=$('#detail .fusion-charts ul.nav-pills li.active a').attr('title');
        var type=$('#fusion-detail-select').val();
        fusionDetail(day,title,type,managerId);
    })


    $('#tixianbtn').click(function(){
        $(this).prop('disabled',true);
        var sel=this;
        setTimeout(function (){
            $(sel).prop('disabled',false);
        },3000);
        $.ajax({
            url:'/tixian',
            type:'POST',
            data:{money:$('#tixianmoney').val(),ip:returnCitySN["cip"]},
            success:function(data){
                console.log(data);
                if(data.timeout==1){
                    location.href="index.html";
                    return;
                }
                getAgentInfo();
                alert(data.msg);
            }
        })
    })

    function getNotice(){
        $.ajax({
            url:'/getNotice',
            success:function(data){
                console.log(data);
                for(var i=0,html='';i<data.length;i++){
                    var o=data[i];
                    html+=`
                        <tr>
                            <td>${o.id}</td>
                            <td>${o.content}</td>
                            <td>${o.managerId||'----'}</td>
                            <td>${o.type==0?'代理公告':(o.type==1?'消息公告':o.type==3?'给全体代理的公告':'全服图片公告')}</td>
                        </tr>
                    `;
                }
                $('#noticeTbl tbody').html(html);
            }
        })
    }

    $('#notice .add-notice').click(function(){
        $('#add-notice').show();
    })
    $('#addNoticeForm .sure').click(function(){
        var content=$('#addNoticeForm [name=content]').val().trim();
        var ntype=$('#addNoticeForm [name=ntype]').val();
        var managerId=$('#addNoticeForm [name=managerId]').val();
        if(content.length==0){
            alert('请输入公告内容！');
            return;
        }
        $.ajax({
            url:'/addNotice',
            data:{content:content,type:ntype,managerId:managerId},
            success:function(data){
                console.log('addnotice');
                console.log(data);
                if(data.status>0){
                    $('#add-notice').hide();
                    alert('公告添加成功！');
                    getNotice();
                }else{
                    alert('公告添加失败！');
                }
            }
        })
    });

    $('#vip .edit').click(function(){
        $('#vipDetail').show();
    })
    $('#vipDetail .sure').click(function(){
        var uuid=$('#vipDetailForm [name=uuid]').val();
        var invitecode=$('#vipDetailForm [name=invitecode]').val();
        console.log(uuid,managerUpId);
        var validUuid=false;
        var validInviteCode=false;
        var managerUpId=0;
        $.ajax({
            url:'/validUuidReManagerUpId',
            async: false,
            data:{uuid:uuid},
            success:function(data){
                console.log(data);
                if(data.validuuid>0){
                    validUuid=true;
                }else{
                    alert('此玩家ID不存在，请重新输入！')
                }
            }
        })
        $.ajax({
            url:'/validInviteCodeReManagerUpId',
            async: false,
            data:{inviteCode:invitecode},
            success:function(data){
                console.log(data);
                if(data.length==1){
                    validInviteCode=true;
                    managerUpId=data[0].id;
                }else{
                    alert('请输入正确的代理邀请码！')
                }
            }
        })
        if(validUuid&&validInviteCode){
            $.ajax({
                url:'/reManagerUpId',
                data:{uuid:uuid,managerUpId:managerUpId},
                success:function(data){
                    console.log(data);
                    if(data.status==1){
                        alert('重新绑定代理邀请码成功！');
                        $('#vipDetail').hide();
                        var page=parseInt($('#vip-pages li.active a').html());
                        getAccount(page);
                    }else{
                        alert('重新绑定代理邀请码失败！')
                    }
                }
            })
        }

    })

    function getManagers2() {
        var starttime = $("#searchAgentForm [name=starttime]").val();
        var endtime = $("#searchAgentForm [name=endtime]").val();
        var managerId = $("#searchAgentForm [name=managerId]").val();
        var uname = $("#searchAgentForm [name=uname]").val();
        var invitecode = $("#searchAgentForm [name=invitecode]").val();
        var powerId = $("#searchAgentForm [name=powerId]").val();
        if (powerId == 0) {
            powerId = ''
        }
        $.ajax({
            url: '/getManagers',
            data: {
                starttime: starttime,
                endtime: endtime,
                managerId: managerId,
                powerId: powerId,
                inviteCode: invitecode,
                uname: uname
            },
            success: function (data) {
                for (var m of data) {
                    m['childAgent'] = [];
                }
                console.dir(data);
                var hash = [];
                for (var i = 0; i < data.length; i++) {
                    if (data[i]['manager_up_id'] == (managerId || sessionStorage['managerId'])) {
                        hash.push(data[i]);
                        data.splice(i, 1);
                        i--;
                    }
                }
                for (var j = 0; j < data.length; j++) {
                    for (var key = 0; key < hash.length; key++) {
                        if (data[j]['manager_up_id'] == hash[key]['id']) {
                            hash[key]['childAgent'].push(data[j]);
                            break;
                        }
                    }
                    if (key < hash.length) {
                        data.splice(j, 1);
                        j--;
                    }
                }
                for (var k = 0; k < data.length; k++) {
                    for (var e = 0; e < hash.length; e++) {
                        for (var n = 0; n < hash[e]['childAgent'].length; n++) {
                            if (data[k]['manager_up_id'] == hash[e]['childAgent'][n]['id']) {
                                hash[e]['childAgent'][n]['childAgent'].push(data[k]);
                                break;
                            }
                        }
                        if (n < hash[e]['childAgent'].length) {
                            break;
                        }
                    }
                    if(e<hash.length){
                        data.splice(k,1);
                        k++;
                    }
                }
            }
        })
    }


});




