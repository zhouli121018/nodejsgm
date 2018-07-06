# coding=utf-8

# 获取比例
def get_rate(unique, total):
    while total:
        return "{}%".format(round((unique * 100.00 / total), 2))
    return '0%'

# 获取最大数
def get_max_data(value):
    max_data = 6
    if 0 < value <= 100:
        max_data = get_max_data_add(value)
    elif 96 < value <= 960:
        max_data = get_max_data_add(int(str(int(value * 1.1))[:-1])) * 10
    elif value > 960:
        max_data = get_max_data_add(int(str(int(value * 1.1))[:-2])) * 100
    return max_data

def get_max_data_add(value):
    for i in range(10):
        if (value + i) % 6 == 0:
            max_data = value + i
            break
    return max_data