# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: utils.py
 @DateTime: 2025-01-22 16:48
 @SoftWare: PyCharm
"""
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


## 函数性能时间计算装饰器
def cost_time(func):
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"当前方法 {func.__name__} cost time {time.perf_counter() - t:.8f}s")
        return result
    return wrapper

## 文件处理工具
import pandas as pd
import os
import json
import math
from snap7 import util

def extract_bit(value, bit_position):
    return (value >> bit_position) & 1

class JsonCache:
    def __init__(self):
        self.cache = {}

    def get_data(self, filename):
        if filename not in self.cache:
            file_name = (filename.split('\\')[-1]).split('.')[0]
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    self.cache[file_name] = json.load(file)
            except FileNotFoundError:
                print(f"Error :{filename} not Found")
                return None
            except json.JSONDecodeError:
                print(f"Error :{filename} contains invalid JSON")
                return None
        return self.cache[file_name]

    def load_from_dir(self, dir_path):
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                full_path = os.path.join(dir_path, filename)
                self.get_data(full_path)


type_mapper = {
    "SHORT": 2,
    "USHORT": 2,
    "FLOAT": 4,
    "LONG": 4,
    "BIT": 1
}


def excel_to_sheet():
    # 读取Excel文件
    excel_path = os.path.join(os.path.dirname(__file__), '数据处理',
                              '500点位.xlsx')
    print("当前文件：", excel_path)
    df = pd.read_excel(excel_path, engine='openpyxl', sheet_name="Sheet1")

    output_excel_path = os.path.join(os.path.dirname(__file__), '数据处理',
                                     '500点位(分组).xlsx')
    # 提取 ItemName 列中的 'DBaa.bb' 中的 aa 部分
    df['Category'] = df['ItemName'].apply(lambda x: str(x).split('.')[0][2:])

    # 获取所有的分类
    categories = df['Category'].unique()

    # 创建一个 Excel writer
    with pd.ExcelWriter(output_excel_path) as writer:
        for category in categories:
            # 根据分类筛选数据
            category_data = df[df['Category'] == category]

            # 将筛选后的数据写入相应的 sheet
            category_data.to_excel(writer, sheet_name=category, index=False)

    print(f"分类后的数据已成功保存到 {output_excel_path}")


## 数据文件读取并处理
def file_take():
    # 定义原始Excel文件的路径
    excel_path = os.path.join(os.path.dirname(__file__), '数据处理', '500点位(分组).xlsx')

    # 读取Excel文件，sheet_name=None表示读取所有工作表
    xls = pd.ExcelFile(excel_path)

    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(__file__), '数据处理')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 定义输出Excel文件的路径
    output_path = os.path.join(output_dir, '分组数据_排序后(500点FEMS).xlsx')

    # 使用ExcelWriter准备写入Excel文件
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # 对每个工作表进行循环处理
        for sheet_name in xls.sheet_names:
            # 读取当前工作表的数据
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # 提取第三列，并提取“.”前的字符串作为DB块，提取“.”后的字符串作为排序依据
            df['DB块'] = df['ItemName'].str.split('.').str[0].str[2:]
            depend = df['ItemName'].str.split('.').str[1:].str.join('.')
            df['排序依据'] = pd.to_numeric(depend)

            # 根据'排序依据'对数据进行排序
            sorted_df = df.sort_values(by='排序依据')

            # 将排序后的数据写回Excel文件的相应工作表，覆盖原有数据
            sorted_df.to_excel(writer, sheet_name=f"DB{sheet_name}", index=False)

    print('处理完成，排序后的文件已保存并覆盖原有工作表。')


## 数据文件转化Json文件
def file_transport():
    import json
    file_path = os.path.join(os.path.dirname(__file__), "数据处理", "分组数据_排序后(500点FEMS).xlsx")
    sheets = pd.read_excel(file_path, sheet_name=None)

    file_path = os.path.join(os.path.dirname(__file__), "500FEMS_json文件")
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    def sheet_to_json(sheet):
        result = {}
        for idx, row in sheet.iterrows():
            tag_name = row['TagName'].split('_')[1:]
            tag_name_key = '_'.join(tag_name)
            result[tag_name_key] = {
                'DB': str(row['Category']),
                'Start': str(row['排序依据']),
                'Type': row['ItemDataType']
            }
        return result

    for sheet_name, sheet_data in sheets.items():
        json_data = sheet_to_json(sheet_data)
        json_file_path = os.path.join(file_path, f"DB{sheet_name}.json")

        with open(json_file_path, 'w', encoding='utf-8') as json_file_path:
            json.dump(json_data, json_file_path, ensure_ascii=False, indent=4)

        print(f"{sheet_name}.json 文件已经生成")


## 获取个json文件中字典数据集
def file_data(file_path):
    # 获取当前飞轮仓DB块，起止地址，总长度
    data_dir = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        first_key = list(data.keys())[0]
        last_key = list(data.keys())[-1]
    data_dir['DB'] = int(data[first_key]['DB'])
    data_dir['starts'] = math.floor(float(data[first_key]['Start']))
    typee = data[last_key]['Type']
    if typee in type_mapper:
        value = type_mapper[typee]
    else:
        raise ValueError(f"Unsupported type:{typee}")
    data_dir['lengths'] = (math.ceil(float(data[last_key]['Start']))) + value
    return data_dir


def get_data(cache_adata, plc_data):
    data_type = cache_adata['Type']
    index = int(cache_adata['Start'].split('.')[0])
    start = int(cache_adata['Start'].split('.')[-1])
    value = 0
    if data_type not in type_mapper:
        raise ValueError(f"{data_type} is not supported")
    try:
        if data_type == 'BIT':
            value = util.get_bool(plc_data, index, start)
        elif data_type == 'USHORT':
            value = util.get_uint(plc_data, index)
        elif data_type == 'SHORT':
            value = util.get_int(plc_data, index)
        elif data_type == 'FLOAT':
            value = util.get_real(plc_data, index)
        elif data_type == 'LONG':
            value = util.get_udint(plc_data, index)
        else:
            print(f"Unsupported data type: {data_type}")
    except Exception as e:
        print(f"数值转化出错:{e}")

    return value


def mian():
    import os
    os.chmod('D:\\pycahrm\\Test1.0\\taosproject\工具类\\data.csv',0o777)
    print("权限修改完成")

    # 处理原始点表数据，分sheet
    excel_to_sheet()
    # 处理分sheet后的excel表，并排序为后期数据查找提供基础
    file_take()
    # 将各排序后的sheet进行json文件转化并存储至文件夹
    file_transport()
    folder_path = os.path.join(os.path.dirname(__file__), 'FEMSjson文件')
    for file_path in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_path)
        data = file_data(file_path)
        print(data)
    print("全部采集点信息打印结束")
    # 使用示例
    cache = JsonCache()
    cache.load_from_dir(folder_path)

    # 打印缓存的数据
    # for file, data in cache.cache.items():
    #     print(f"Data from {file}: {data}")

    cache_data = cache.cache.get(f"DB12block")
    for key in cache_data:
        print(key)

