"""
@File  : modbus_converter.py
@Author: lee
@Date  : 2022/7/12/0012 8:55:13
@Desc  : 此类为modbus协议通用解析器，用于：insitu水质传感器，新气象传感器，新水质传感器
"""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from datetime import datetime
from datetime import timedelta

app = FastAPI()

# 配置允许域名
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1"
]
# 配置允许域名列表、允许方法、请求头、cookie等
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# hui_yi_shui_zhi
# shucai
# 连接Perf_show数据库
register_tortoise(
    app,
    db_url='mysql://root:123456@127.0.0.1:3306/shucai_huiyi',
    modules={"models": []},
    generate_schemas=True,
    add_exception_handlers=True,
)

"""
时间：2022-08-29
功能：获取最新一条数据
----------------------------------------------------------------
"""


@app.post("/realTime/getRealTimeNewData")
async def get_real_time_new_data():
    db = Tortoise.get_connection("default")
    query = "SELECT ROUND( c1, 2 ) as c1,ROUND(c2, 2 ) as c2,ROUND(c3,2 ) as c3," \
            "ROUND( c4, 2 ) as c4,ROUND(c5, 2 ) as c5,ROUND(c6,2 ) as c6  " \
            "FROM `table_shuizhi` " \
            "ORDER BY times DESC LIMIT 1"
    result = await db.execute_query_dict(query)

    query = "SELECT ROUND( c7, 2 ) as c7 " \
            "FROM `table_yelvsu` " \
            "ORDER BY times DESC LIMIT 1"
    get_yelvsu = await db.execute_query_dict(query)
    result[0]['c7'] = get_yelvsu[0]['c7']
    return result


"""
时间：2022-08-29
功能：获取24小时内参数的最大最小平均值
----------------------------------------------------------------
"""


@app.post("/realTime/getNameMaxMinAvgData")
async def get_max_min_avg_data():
    db = Tortoise.get_connection("default")

    nowTime = datetime.now()
    oneDayBeforeTime = nowTime + timedelta(days=-1)
    # sevenDayBeforeTime = nowTime + timedelta(days=-7)

    nowTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
    oneDayBeforeTime = oneDayBeforeTime.strftime('%Y-%m-%d %H:%M:%S')
    # sevenDayBeforeTime = sevenDayBeforeTime.strftime('%Y-%m-%d %H:%M:%S')

    dataName = ['c1', 'c2', 'c3', 'c4', 'c6', 'c5', 'c7']
    result = []
    for i in range(len(dataName)):
        if dataName[i] != 'c7':
            query = f"SELECT ROUND(AVG({dataName[i]}),2 ) AS avgVal," \
                    f"ROUND(MAX({dataName[i]}),2 ) AS maxVal," \
                    f"ROUND(MIN({dataName[i]}),2 ) AS minVal " \
                    "FROM `table_shuizhi` " \
                    f"WHERE times >= '{oneDayBeforeTime}' and times <= '{nowTime}'"
            temp = await db.execute_query_dict(query)
            temp[0]['name'] = dataName[i]
            result.append(temp[0])
        else:
            query = f"SELECT ROUND(AVG({dataName[i]}),2 ) AS avgVal," \
                    f"ROUND(MAX({dataName[i]}),2 ) AS maxVal," \
                    f"ROUND(MIN({dataName[i]}),2 ) AS minVal " \
                    "FROM `table_yelvsu` " \
                    f"WHERE times >= '{oneDayBeforeTime}' and times <= '{nowTime}'"
            temp = await db.execute_query_dict(query)
            temp[0]['name'] = dataName[i]
            result.append(temp[0])
    return result


"""
时间: 2022/8/30
功能: 返回实时数据请求的echarts用到的数据
----------------------------------------------------------------
"""


class realTimeEchart(BaseModel):
    dateType: str = "hour"
    dataName: str = "Tur"


@app.post("/realTime/getEchartsDatas")
async def get_echarts_datas(realTimeEchart: realTimeEchart):
    db = Tortoise.get_connection("default")
    dateType = realTimeEchart.dateType
    dataName = realTimeEchart.dataName
    sqlDataName = {'Tem': 'c1', 'Sal': 'c2', 'Deep': 'c3', 'Tur': 'c4', 'Do': 'c6', 'Ph': 'c5', 'Chl': 'c7'}

    # 获取现在、24小时前、7天前和30天前的时间
    nowTime = datetime.now()
    oneDayBeforeTime = nowTime + timedelta(days=-1)
    sevenDayBeforeTime = nowTime + timedelta(days=-7)
    thirtyDayBeforeTime = nowTime + timedelta(days=-30)
    # 格式化时间
    nowTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
    oneDayBeforeTime = oneDayBeforeTime.strftime('%Y-%m-%d %H:%M:%S')
    sevenDayBeforeTime = sevenDayBeforeTime.strftime('%Y-%m-%d %H:%M:%S')
    thirtyDayBeforeTime = thirtyDayBeforeTime.strftime('%Y-%m-%d %H:%M:%S')

    if dataName != 'Chl':
        # 判断请求的时间段并返回请求数据
        if dateType == "hour":
            query = f"SELECT times,ROUND({sqlDataName[dataName]},2) {sqlDataName[dataName]} FROM `table_shuizhi` " \
                    f"WHERE times >= '{oneDayBeforeTime}' and times <= '{nowTime}'"
        elif dateType == "week":
            query = f"SELECT times,ROUND({sqlDataName[dataName]},2) {sqlDataName[dataName]} FROM `table_shuizhi` " \
                    f"WHERE times >= '{sevenDayBeforeTime}' and times <= '{nowTime}'"
        elif dateType == "month":
            query = f"SELECT times,ROUND({sqlDataName[dataName]},2) {sqlDataName[dataName]} FROM `table_shuizhi` " \
                    f"WHERE times >= '{thirtyDayBeforeTime}' and times <= '{nowTime}'"
        else:
            return {'msg': 'dateType error'}
    else:
        # 判断请求的时间段并返回请求数据
        if dateType == "hour":
            query = f"SELECT times,ROUND({sqlDataName[dataName]},2) {sqlDataName[dataName]} FROM `table_yelvsu` " \
                    f"WHERE times >= '{oneDayBeforeTime}' and times <= '{nowTime}'"
        elif dateType == "week":
            query = f"SELECT times,ROUND({sqlDataName[dataName]},2) {sqlDataName[dataName]} FROM `table_yelvsu` " \
                    f"WHERE times >= '{sevenDayBeforeTime}' and times <= '{nowTime}'"
        elif dateType == "month":
            query = f"SELECT times,ROUND({sqlDataName[dataName]},2) {sqlDataName[dataName]} FROM `table_yelvsu` " \
                    f"WHERE times >= '{thirtyDayBeforeTime}' and times <= '{nowTime}'"
        else:
            return {'msg': 'dateType error'}

    # 数据库获取数据
    getData = await db.execute_query_dict(query)

    # 将时间数据提取成数组
    resultTime = []
    resultData = []
    for i in range(len(getData)):
        resultTime.append(str(getData[i]['times']))
        resultData.append(getData[i][sqlDataName[dataName]])

    # 将提取的数据编成字典返回
    result = {'time': resultTime, 'value': resultData}

    return result


"""
时间: 2022/8/30
功能: 返回历史数据请求的表格数据
----------------------------------------------------------------
"""


class dateStartEnd(BaseModel):
    Start: str = "2022-09-22"
    End: str = "2022-09-22"


@app.post("/history/getHistoryTableData")
async def get_history_table_data(dateStartEnd: dateStartEnd):
    db = Tortoise.get_connection("default")
    start_time = dateStartEnd.Start
    end_time = dateStartEnd.End

    if start_time == end_time:
        query = f"SELECT id,times,ROUND(c1,2) c1,ROUND(c2,2) c2,ROUND(c3,2) c3," \
                f"ROUND(c4,2) c4,ROUND(c5,2) c5,ROUND(c6,2) c6 " \
                f"FROM `table_shuizhi` WHERE date_format(times,'%Y-%m-%d')='{start_time}' ORDER BY times DESC;"
    else:
        query = f"SELECT id,times,ROUND(c1,2) c1,ROUND(c2,2) c2,ROUND(c3,2) c3," \
                f"ROUND(c4,2) c4,ROUND(c5,2) c5,ROUND(c6,2) c6 " \
                f"FROM `table_shuizhi` WHERE times >= '{start_time} 00:00:00' AND times <= '{end_time} 23:59:59' ORDER BY times DESC;"
    result = await db.execute_query_dict(query)

    if start_time == end_time:
        query = f"SELECT id,times,ROUND(c7,2) c7 FROM `table_yelvsu` WHERE date_format(times,'%Y-%m-%d')='{start_time}';"
    else:
        query = f"SELECT id,times,ROUND(c7,2) c7 FROM `table_yelvsu` WHERE times >= '{start_time} 00:00:00' AND times <= '{end_time} 23:59:59';"
    get_yelvsu = await db.execute_query_dict(query)

    for i in range(len(result)):
        result[i]['c7'] = get_yelvsu[i]['c7']
        result[i]['times'] = str(result[i]['times'])

    return result


"""
时间: 2022/8/311
功能: 返回历史数据请求的echarts数据
----------------------------------------------------------------
"""


class hisEchNameStartEnd(BaseModel):
    Name: str = "温度"
    Start: str = "2022-08-30"
    End: str = "2022-08-30"


@app.post("/history/getEchartsDatas")
async def get_echarts_datas(hisEchNameStartEnd: hisEchNameStartEnd):
    db = Tortoise.get_connection("default")
    name = hisEchNameStartEnd.Name
    start_time = hisEchNameStartEnd.Start
    end_time = hisEchNameStartEnd.End
    sqlDataName = {'温度': 'c1', '盐度': 'c2', '水深': 'c3', '浊度': 'c4', '溶解氧': 'c6', 'PH值': 'c5', '叶绿素': 'c7'}

    if name != '叶绿素':
        if (start_time == end_time):
            query = f"SELECT times,ROUND({sqlDataName[name]},2) {sqlDataName[name]} FROM `table_shuizhi` WHERE date_format(times,'%Y-%m-%d')='{start_time}';"
        else:
            query = f"SELECT times,ROUND({sqlDataName[name]},2) {sqlDataName[name]} FROM `table_shuizhi` WHERE times >= '{start_time} 00:00:00' AND times <= '{end_time} 23:59:59';"
    else:
        if (start_time == end_time):
            query = f"SELECT times,ROUND({sqlDataName[name]},2) {sqlDataName[name]} FROM `table_yelvsu` WHERE date_format(times,'%Y-%m-%d')='{start_time}';"
        else:
            query = f"SELECT times,ROUND({sqlDataName[name]},2) {sqlDataName[name]} FROM `table_yelvsu` WHERE times >= '{start_time} 00:00:00' AND times <= '{end_time} 23:59:59';"

    # 数据库获取数据
    getData = await db.execute_query_dict(query)
    # 将时间数据提取成数组
    resultTime = []
    resultData = []
    for i in range(len(getData)):
        resultTime.append(str(getData[i]['times']))
        resultData.append(getData[i][sqlDataName[name]])

    # 将提取的数据编成字典返回
    result = {}
    result['time'] = resultTime
    result['value'] = resultData

    return result


# -------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )
