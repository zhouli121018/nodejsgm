/**
 * Created by zhouli on 2017/5/28.
 */
const http=require('http');
const express=require('express');
const mysql=require('mysql');
const qs=require('querystring');
var pool=mysql.createPool({
    host:'127.0.0.1',
    user:'root',
    password:'',
    database:'myitem',
    connectionLimit:10
});
var app=express();
var server=http.createServer(app);
server.listen(8081);
app.use(express.static('./public'));

//获取商品详情
app.get('/detail',(req,res)=>{
    var p=req.query.src;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT * FROM t_product WHERE pic=?',[p],(err,result)=>{
                if(result!=null){
                    res.json(result[0]);
                }
            })
        }
        conn.release();
    })
});

//翻页，上一个商品，下一个商品
app.get('/detail_pn',(req,res)=>{
    var pid=req.query.pid;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT * FROM t_product WHERE pid=?',[pid],(err,result)=>{
                if(result!=null){
                    res.json(result[0]);
                }
            })
        }
        conn.release();
    })
});

//加入购物车
app.post('/add_shoppingCart',(req,res)=>{
    //console.log(req);
    req.on("data",(buff)=>{
        var obj=qs.parse(buff.toString());
        //console.log(obj);
        var pid=obj.pid;
        var uid=obj.uid;
        var count=parseInt(obj.count);
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('SELECT * FROM t_shoppingCart WHERE uid=? AND pid=?',[uid,pid],(err,result)=>{
                    if(result.length==0){
                        conn.query('INSERT INTO t_shoppingCart VALUES(null,?,?,?)',[uid,pid,count],(err,result)=>{
                            if(err){
                                console.log(err);
                            }else{
                                console.log(result);
                                res.send({"code":1,"msg":"加入购物车成功！","sid":result.insertId});
                            }
                            conn.release();
                        })
                    }else{
                        var scount=result[0].scount;
                        var sid=parseInt(result[0].sid);
                        var c=scount+count;
                        //console.log(result);
                        //console.log(sid,scount);
                        conn.query("UPDATE t_shoppingCart SET scount=? WHERE sid=?",[c,sid],(err,result)=>{
                            console.log(result);
                            res.send({"code":2,"msg":"加入购物车成功！"})
                        })
                    }
                });

            }
        })
    });

});

//立即购买
//app.post('/buy',(req,res)=>{
//
//}


//注册
app.get('/reg_user',(req,res)=>{
    var uname=req.query.uname;
    var upwd=req.query.upwd;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT * FROM t_user WHERE uname=?',[uname],(err,result)=>{
                if(err){
                    console.log(err);
                }else{
                    if(result.length!=0){
                        res.send({"code":-2,"msg":"此用户名已存在！"})
                    }else{
                        conn.query('INSERT INTO t_user VALUES(null,?,?,now())',[uname,upwd],(err,result)=>{
                            if(err){
                                console.log(err);
                            }else{
                                var data={code:200,msg:'注册成功！去登录...'};
                                res.json(data);
                            }
                        })
                    }
                }
                conn.release();
            })

        }
    })
});

//登录
app.get('/login_user',(req,res)=>{
    var uname=req.query.uname;
    var upwd=req.query.upwd;
    pool.getConnection((err,conn)=>{
        if(err){
            console.log(err);
        }else{
            conn.query('SELECT * FROM t_user WHERE uname=? AND upwd=?',[uname,upwd],(err,result)=>{
                if(err){
                    console.log(err);
                }else{
                    //console.log(result);
                    if(result.length==0){
                        res.send({"code":-1,"msg":"用户名或密码不存在！"})
                    }else{
                        res.send({"code":1,"msg":"登录成功！","uid":result[0].uid,"uname":result[0].uname});
                    }
                }
                conn.release();
            })
        }
    })
});

//获取购物车 数量
app.get('/shoppingCart/count',(req,res)=>{
    var uid=req.query.uid;
    pool.getConnection((err,conn)=>{
        conn.query('SELECT sum(scount) AS c FROM t_shoppingCart WHERE uid=?',[uid],(err,result)=>{
            //console.log(result);
            res.json(result[0]);
            conn.release();
        })
    })
});

//获取购物车详情
app.get('/shoppingCart-list',(req,res)=>{
    var uid=req.query.uid;
    pool.getConnection((err,conn)=>{
        conn.query('SELECT p.pic,p.pname,p.price,s.sid,s.scount,p.pid FROM t_shoppingCart s,t_product p WHERE  s.pid=p.pid AND s.uid=?',[uid],(err,result)=>{
            res.json(result);
            conn.release();
        })

    })
});

//修改购物车数量
app.get('/add_count',(req,res)=>{
   var sid=req.query.sid;
    pool.getConnection((err,conn)=>{
        conn.query('UPDATE t_shoppingcart SET scount=scount+1 WHERE sid=?',[sid],(err,result)=>{
            if(err){
                console.log(err);
                res.send({"code":-1,"msg":"修改购物车失败！"})
            }else{
                res.send({"code":1,"msg":"修改购物车成功！"})
            }
        })
    })
});

app.get('/min_count',(req,res)=>{
    var sid=req.query.sid;
    pool.getConnection((err,conn)=>{
        conn.query('UPDATE t_shoppingcart SET scount=scount-1 WHERE sid=?',[sid],(err,result)=>{
            if(err){
                console.log(err);
                res.send({"code":-1,"msg":"修改购物车失败！"})
            }else{
                res.send({"code":1,"msg":"修改购物车成功！"})
            }
            conn.release();
        })
    })
});

//删除购物车信息
app.get('/delete-shoppingCart',(req,res)=>{
    var sid=req.query.sid;
    pool.getConnection((err,conn)=>{
        conn.query('DELETE FROM t_shoppingCart WHERE sid=?',[sid],(err,result)=>{
            if(err){
                var data={code:-1,msg:'删除失败！'}
            }else{
                var data={code:1,msg:'删除成功！'}
            }
            res.json(data);
            conn.release();
        })
    })
});

//用户中心
app.get('/order/list',(req,res)=>{
   var uid=req.query.uid;
    console.log(uid);
    pool.getConnection((err,conn)=>{
        conn.query('SELECT * FROM t_order WHERE userId=?',[uid],(err,orderList)=>{
            console.log(orderList);
            var progress=0;
            for(let order of orderList){
                conn.query('SELECT * FROM t_product WHERE pid IN (SELECT productId FROM t_order_detail WHERE orderId=?)',[order.oid],(err,plist)=>{
                    order['productList']=plist;
                    progress++;
                    if(progress===orderList.length){
                        console.log(orderList);
                        res.json(orderList);
                        conn.release();
                    }
                });
            }


        })
    })
});


//搜索关键字
app.get('/search/product',(req,res)=>{
    var kw=req.query.kw;
    var k='%'+kw+'%';
    pool.getConnection((err,conn)=>{
        conn.query("SELECT * FROM t_product WHERE pname LIKE ?",[k],(err,result)=>{
            console.log(result);
            res.json(result);
            conn.release();
        })
    })
});

//提交订单
app.post('/submitOrder',(req,res)=>{
    req.on("data",(buff)=>{
        var obj=qs.parse(buff.toString());
        console.log(obj);
        console.log(typeof obj.orderDetails,obj.orderDetails);
        var orderObj=eval('('+obj.orderDetails+')');
        var uid=obj.uid;
        var rcv=obj.rcvname;
        var price=obj.price;
        var payment=obj.payment;
        pool.getConnection((err,conn)=>{
            if(err){
                console.log(err);
            }else{
                conn.query('INSERT INTO t_order VALUES(NULL,?,?,?,now(),1,?)',[rcv,price,payment,uid],(err,result)=>{
                         //console.log(result);
                        var oid=result.insertId;
                    for(var i=0;i<orderObj.length;i++){
                        var o=orderObj[i];
                        var pid=o.pid,count=o.count;
                        console.log(pid,count,oid);
                        conn.query('INSERT INTO t_order_detail VALUES(NULL,?,?,?)',[oid,pid,count],(err,result)=>{
                            console.log(result);
                        })
                    }
                    res.json({"code":200,"oid":result.insertId});
                    conn.release();
                });

            }
        })
    });
});

//获取消费数据
app.get('/order/buystat',(req,res)=>{
    var data = [
        {label: '6月', value: 3500},
        {label: '7月', value: 2500},
        {label: '8月', value: 5000},
        {label: '9月', value: 4000},
        {label: '10月', value: 500},
        {label: '11月', value: 5500},
        {label: '12月', value: 7000},
        {label: '1月', value: 3000},
        {label: '2月', value: 4000},
        {label: '3月', value: 5000},
        {label: '4月', value: 3800},
        {label: '5月', value: 4300}
    ];
    res.json(data);
});

