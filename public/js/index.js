/**
 * Created by 51216 on 2017/11/22.
 */


$(function(){
    if(sessionStorage['loginInviteCode']){
        console.log(1);
    }else{
        location.href="index.html";
    }

    $('#tablist li a').click(function(e){
        if ( e && e.preventDefault )
            e.preventDefault();
        else
            window.event.returnValue = false;
        var id=$(this).attr('href');
        if(id=="#agent"){
            getManagers();
        }else if(id=="#vip"){
            getAccounts();
        }else if(id=="#detail"){
            getDetails();
        }else if(id=="#info"){
            getAgentInfo();
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
    }
    function getManagers(){
        $.ajax({
            url:'/getManagers',
            data:{managerId:15},
            success:function(data){
                console.dir(data);
                var totalpages=1;
                if(data.length%10==0){
                    totalpages=parseInt(data.length/10);
                }else{
                    totalpages=parseInt(data.length/10)+1;
                }

                var options = {
                    currentPage: 1,
                    totalPages:totalpages,
                    bootstrapMajorVersion: 3,
                    onPageChanged: function(e,oldPage,newPage){
                        var start=(newPage-1)*10;
                        var end=start+parseInt(10);
                        if(end>data.length)end=data.length;
                        rendAgent(start,end);
                    }
                };

                $('#agent-pages').bootstrapPaginator(options);
                $('#agent .total-number').html(data.length);
                var initend=10;
                if(initend>data.length)initend=data.length;
                rendAgent(0,initend);
                function rendAgent(start,end){
                    for(var i=start,html='';i<end;i++){
                        var o=data[i];
                        if(data[i].agentNumber>0){
                            html+=`
                    <tr>
                        <td data-level="1" class="childAgent level1"><span class="tree-collapse"></span><b>${o.id}</b></td>`;
                        }else{
                            html+=`
                    <tr>
                        <td data-level="1" class="level1"><span></span><b>${o.id}</b></td>`;
                        };

                        html+=`
                    <td>${o.name}</td>
                    <td>${o.uuid}</td>
                    <td>${o.nickName}</td>
                    <td>${o.power_id==5?'皇冠代理':(o.power_id==4?'钻石代理':(o.power_id==3?'铂金代理':(o.power_id==2?'黄金代理':'系统管理员')))}</td>

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


            }
        });
    }
    function getAccounts(){
        $.ajax({
            url:'/getAccounts',
            data:{managerId:15},
            success:function(data){
                console.dir(data);

                var totalpages=1;
                if(data.length%10==0){
                    totalpages=parseInt(data.length/10);
                }else{
                    totalpages=parseInt(data.length/10)+1;
                }

                var options = {
                    currentPage: 1,
                    totalPages:totalpages,
                    bootstrapMajorVersion: 3,
                    onPageChanged: function(e,oldPage,newPage){
                        var start=(newPage-1)*10;
                        var end=start+parseInt(10);
                        if(end>data.length)end=data.length;
                        rendAccounts(start,end);
                    }
                };

                $('#vip-pages').bootstrapPaginator(options);
                $('#vip .total-number').html(data.length);
                var initend=10;
                if(initend>data.length)initend=data.length;
                rendAccounts(0,initend);

                function rendAccounts(start,end){
                    for(var i=start,html='';i<end;i++){
                        var o=data[i];
                        html+=`
                <tr>
                    <td>${o.uuid}</td>
                    <td>${o.nickName}</td>
                    <td>${o.sumMoney}</td>
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
            }
        });
    }

    function getDetails(){
        $.ajax({
            url:'/getDetails',
            data:{managerId:15},
            success:function(data){
                console.dir(data);
                var totalpages=1;
                if(data.length%10==0){
                    totalpages=parseInt(data.length/10);
                }else{
                    totalpages=parseInt(data.length/10)+1;
                }

                var options = {
                    currentPage: 1,
                    totalPages:totalpages,
                    bootstrapMajorVersion: 3,
                    onPageChanged: function(e,oldPage,newPage){
                        var start=(newPage-1)*10;
                        var end=start+parseInt(10);
                        if(end>data.length)end=data.length;
                        rendDetails(start,end);
                    }
                };

                $('#detail-pages').bootstrapPaginator(options);
                $('#detail .total-number').html(data.length);
                var initend=10;
                if(initend>data.length)initend=data.length;
                rendDetails(0,initend);

                function rendDetails(start,end){
                    for(var i=start,html='';i<end;i++){
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


            }
        })
    }
    getAgentInfo();

    function resetPassword(){

    }




    function getChildAgents(id,ele,level){
        console.log(id);
        $.ajax({
            url:'/getChildAgents',
            data:{managerId:id},
            success:function(data){
                console.dir(data);
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
                    <td>${o.power_id==5?'皇冠代理':(o.power_id==4?'钻石代理':(o.power_id==3?'铂金代理':(o.power_id==2?'黄金代理':'系统管理员')))}</td>

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
                ele.after(html);
            }
        })
    }
    $("#agent #agentTbl tbody").on("click",'td span.tree-collapse',function(){
        var mid=$(this).next().html();
        var ele=$(this).parents('tr');
        $(this).removeClass('tree-collapse').addClass('tree-expend');
        var level=parseInt($(this).parents('td').attr('data-level'))+1;
        getChildAgents(mid,ele,level);
    })
    $("#agent #agentTbl tbody").on("click",'td span.tree-expend',function(){
        var mid=$(this).next().html();
        $(this).removeClass('tree-expend').addClass('tree-collapse');
        $("#agentTbl [data-parent='"+mid+"']").hide();
    })


});