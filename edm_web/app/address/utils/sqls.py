# coding=utf-8

# 清空地址库
def deleteAddress(cr, tablename, list_id):
    sql = u"DELETE FROM {0} WHERE list_id={1}".format(tablename, list_id)
    cr.execute(sql)
    return

# 设置分类为：id， 合并订阅地址
def updateAddressListID(cr, tablename, list_id, list_ids_str):
    sql = u"UPDATE {0} SET list_id={1} WHERE list_id in ({2})".format(tablename, list_id, list_ids_str)
    cr.execute(sql)
    return

# 合并 退订地址
def updateUnsubAddrID(cr, user_id, list_id, list_ids_str):
    sql = u"UPDATE ml_unsubscribe_{0} SET list_id={1} WHERE list_id in ({2})".format(user_id, list_id, list_ids_str)
    cr.execute(sql)
    return

# 剔除重复邮箱地址
def deleteRepeatAddress(cr, tablename, list_id):
    sql = u"""
    DELETE a.* FROM {0} AS a, (
            SELECT address, COUNT(*), MAX(address_id) AS address_id
              FROM {0} WHERE list_id={1}
              GROUP BY address HAVING COUNT(*)>1
            ) AS b
    WHERE list_id={1} AND a.address=b.address and a.address_id < b.address_id;
    """.format(tablename, list_id)
    cr.execute(sql)
    return

# #### 查询是否存在订阅记录 #####
def select_address(cr, tablename, address, list_id):
    cr.execute(
        u"SELECT address_id FROM {0} WHERE address='{1}' AND list_id={2} LIMIT 1;".format(tablename, address, list_id))
    return cr.fetchone()

# #### 更新订阅记录 #####
def update_address(cr, tablename, address, list_id):
    cr.execute(
        u"UPDATE {0} SET is_subscribe=1 WHERE address='{1}' AND list_id={2};".format(tablename, address, list_id))
    return u'您已经订阅过此邮件列表！\n(You have subscribed to the mail list)'

# #### 插入订阅记录 #####
def insert_address(cr, tablename, **kwargs):
    sql = u"""INSERT INTO {} (created,is_subscribe,list_id,address,fullname,sex,birthday,phone,area,var1,var2,var3,var4,var5,var6,var7,var8,var9,var10)
              VALUES (now(),1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""".format(tablename)
    fields = ['list_id', 'address', 'fullname', 'sex', 'birthday', 'phone', 'area', 'var1', 'var2', 'var3', 'var4', 'var5', 'var6', 'var7', 'var8', 'var9', 'var10']
    args = []
    for f in fields:
        args.append(kwargs.get(f, ''))
    cr.execute(sql, args)

    # cr.execute(
    #     u"-- INSERT INTO {0} (address, fullname, created, is_subscribe, list_id) VALUES ('{1}', '{2}', now(), 1, {3});".format(
    #         tablename, address, fullname, list_id)
    # )
    return u'订阅成功！\n(Success)'

def get_addr_count(cr, user_id, list_id, status):
    """ 统计 用户地址池数量
    :param cr:
    :param user_id:
    :param list_id:
    :param status:  1.地址池总量  2.地址池订阅数量  3.退订数量  4.投诉数量
    :return:
    """
    count = 0
    if status == '1':
        try:
            sql = "SELECT COUNT(1) FROM ml_subscriber_{} WHERE list_id={};".format(user_id, list_id)
            cr.execute(sql)
            data = cr.fetchone()
            count = data[0] if data else 0
        except:
            pass
    elif status == '2':
        try:
            sql = "SELECT COUNT(1) FROM ml_subscriber_{} WHERE list_id={} AND is_subscribe=1;".format(user_id, list_id)
            cr.execute(sql)
            data = cr.fetchone()
            count = data[0] if data else 0
        except:
            pass
    elif status == '3':
        try:
            sql = "SELECT COUNT(1) FROM ml_unsubscribe_{} WHERE list_id={};".format(user_id, list_id)
            cr.execute(sql)
            data = cr.fetchone()
            count = data[0] if data else 0
        except:
            pass
    return count

# 检测表格是否存在
def checkTable(cr, customer_id):
    # sql = 'SHOW TABLES LIKE "ml_subscriber_{}"'.format(customer_id)
    sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='mm-pool' AND TABLE_NAME='ml_subscriber_{}';".format(customer_id)
    res = cr.execute(sql)
    if not res:
        create_sql = """CREATE TABLE IF NOT EXISTS `ml_subscriber_{}` (
                      `address_id` int(11) NOT NULL AUTO_INCREMENT,
                      `list_id` int(11) NOT NULL DEFAULT '0',
                      `address` varchar(50) DEFAULT NULL,
                      `fullname` varchar(100) DEFAULT NULL,
                      `var1` varchar(100) DEFAULT NULL,
                      `var2` varchar(100) DEFAULT NULL,
                      `var3` varchar(100) DEFAULT NULL,
                      `var4` varchar(100) DEFAULT NULL,
                      `var5` varchar(100) DEFAULT NULL,
                      `var6` varchar(100) DEFAULT NULL,
                      `var7` varchar(100) DEFAULT NULL,
                      `var8` varchar(100) DEFAULT NULL,
                      `var9` varchar(100) DEFAULT NULL,
                      `var10` varchar(100) DEFAULT NULL,
                      `created` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
                      `is_subscribe` tinyint(1) NOT NULL DEFAULT '0',
                      `sex` varchar(8) DEFAULT NULL COMMENT '性别',
                      `birthday` date NOT NULL DEFAULT '0000-00-00' COMMENT '生日',
                      `phone` varchar(100) DEFAULT NULL COMMENT '手机',
                      `activity` int(11) NOT NULL DEFAULT '0' COMMENT '活跃度（1-5颗星星，默认五颗灰色的星星，打开一次一颗）',
                      `area` varchar(200) DEFAULT NULL COMMENT '所在地域',
                      `updated` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '更新时间',
                      KEY `address_id` (`address_id`),
                      KEY `address` (`address`),
                      KEY `list_id` (`list_id`)
                    ) ENGINE=MyISAM  DEFAULT CHARSET=utf8
                    PARTITION BY LINEAR HASH(`list_id`)
                    PARTITIONS 3 ;""".format(customer_id)
        cr.execute(create_sql)
    # sql = 'SHOW TABLES LIKE "ml_unsubscribe_{}"'.format(customer_id)
    sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='mm-pool' AND TABLE_NAME='ml_unsubscribe_{}';".format(customer_id)
    res = cr.execute(sql)
    if not res:
        create_sql = """CREATE TABLE IF NOT EXISTS `ml_unsubscribe_{}` (
                      `list_id` int(11) NOT NULL DEFAULT '0',
                      `address` varchar(50) DEFAULT NULL,
                      `datetime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
                      KEY `list_id` (`list_id`),
                      KEY `datetime` (`datetime`)
                    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;""".format(customer_id)
        cr.execute(create_sql)
