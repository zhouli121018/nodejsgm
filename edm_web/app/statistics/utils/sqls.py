# -*- coding:utf-8 -*-

def get_statistics_sql(customer_id, date_start, date_end, order_by_str=''):
    sql = u'''
    SELECT core.username, stat.task_date, core.company,
            -- Web发送量统计
            CAST(COALESCE(task.count_send, 0) AS SIGNED) AS count_send,     -- 任务量
            CAST(COALESCE(task.count_error, 0) AS SIGNED) AS count_error,   -- 失败量
            CAST(COALESCE(task.count_succes, 0) AS SIGNED) AS count_succes, -- 发送量

            -- 错误地址
            CAST(COALESCE(error.error_type_9, 0) AS SIGNED) AS error_type_9,     -- 格式错误
            CAST(COALESCE(error.error_type_8, 0) AS SIGNED) AS error_type_8,     -- 无效地址

            -- 预统计/扣点
            CAST(COALESCE(stat.count_send_exp, 0) AS SIGNED) AS count_send_exp,     -- 发送量
            CAST(COALESCE(deduction.point_exp, 0) AS SIGNED) AS point_exp,          -- 预扣点

            -- 实际统计/扣点
            CAST(COALESCE(stat.count_send_real, 0) AS SIGNED) AS count_send_real,     -- 实际发送
            CAST(COALESCE(stat.count_fail, 0) AS SIGNED) AS count_fail,               -- 投递失败
            CAST(COALESCE(stat.count_err_5, 0) AS SIGNED) AS count_err_5,             -- 拒绝投递
            CAST(COALESCE(deduction.point_exp, 0) AS SIGNED) - stat.rebate AS point_real -- 实际扣点
    FROM (
         SELECT customer_id, username, company FROM core_customer WHERE customer_id={0}
    ) core
    LEFT JOIN (
        SELECT customer_id, task_date,
                -- 预统计/扣点
                SUM(count_send) - SUM(count_error) + SUM(count_err_1) + SUM(count_err_2) + SUM(count_err_3) + SUM(count_err_5) AS count_send_exp, -- 发送量
                -- 实际统计/扣点
                SUM(count_send) - SUM(count_error) AS count_send_real, -- 实际发送
                SUM(count_err_1) + SUM(count_err_2) + SUM(count_err_3) AS count_fail,-- 投递失败
                SUM(count_err_5) AS count_err_5,    -- 拒绝投递
                SUM(rebate) AS rebate -- 返点量
        FROM stat_task
        WHERE customer_id={0} AND task_date BETWEEN '{1}' AND '{2}'
        GROUP BY customer_id, task_date
    ) stat ON stat.customer_id = core.customer_id
    LEFT JOIN (
         -- Web发送量统计
         SELECT customer_id, task_date,
                 SUM(send_qty_remark) AS count_send, -- 任务量
                 SUM(error_count) AS count_error,    -- 失败量
                 SUM(send_count) AS count_succes     -- 发送量
         FROM (
              SELECT user_id AS customer_id, DATE_FORMAT(send_time, '%Y-%m-%d') task_date, send_qty_remark, send_count, error_count
              FROM ms_send_list
              WHERE user_id={0} AND send_status='3' AND send_time BETWEEN '{1} 00:00:00' AND '{2} 23:59:59'
         ) task_data
         GROUP BY customer_id, task_date
    ) task ON task.customer_id = stat.customer_id AND task.task_date = stat.task_date
    LEFT JOIN (
        SELECT customer_id, task_date,
                    MAX(CASE error_type WHEN 8 THEN error_count ELSE 0 END ) error_type_8,
                    MAX(CASE error_type WHEN 9 THEN error_count ELSE 0 END ) error_type_9
        FROM (
                -- 错误地址, 需要行专列
                SELECT customer_id, send_date AS task_date, COUNT(DISTINCT recipient) AS error_count, error_type
                FROM stat_error_list
                WHERE customer_id={0} AND send_date BETWEEN '{1}' AND '{2}' AND error_type in (8, 9)
                GROUP BY customer_id, send_date, error_type
        ) error_data
        GROUP BY customer_id, task_date
    ) error ON error.customer_id = stat.customer_id AND error.task_date = stat.task_date
    LEFT JOIN (
        SELECT customer_id, date, SUM(point_exp) AS point_exp
        FROM (
                -- 预扣点
                SELECT customer_id, date, deduction*count AS point_exp
                FROM stat_deduction
                WHERE customer_id={0} AND date BETWEEN '{1}' AND '{2}'
        ) point_exp_data
        GROUP BY customer_id, date
    ) deduction ON deduction.customer_id = stat.customer_id AND deduction.date = stat.task_date
    WHERE stat.customer_id IS NOT NULL
    {3}
    '''.format(customer_id, date_start, date_end, order_by_str)
    return sql