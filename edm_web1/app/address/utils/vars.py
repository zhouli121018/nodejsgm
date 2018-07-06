# coding=utf-8

import re

def get_addr_var_fields(cr, customer_id):
    self_var_pattern = re.compile('var\d+')
    sql = "SELECT column_name FROM information_schema.COLUMNS WHERE table_name = 'ml_subscriber_{}' AND table_schema = 'mm-pool';".format(customer_id)
    cr.execute(sql)
    res = cr.fetchall()
    var_lists = sorted(filter(lambda s: self_var_pattern.match(s), [r[0] for r in res]), key=lambda k: int(k[3:]))
    return var_lists

def get_fields_args(database_fields, field):
    process_len = min(len(database_fields), len(field))
    sql_part = "=%s,".join(database_fields[:process_len])
    if sql_part:
        sql_part = ',' + sql_part + "=%s"
    args = field[:process_len]
    return sql_part, args