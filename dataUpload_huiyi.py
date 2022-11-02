#!/usr/bin/env python
# encoding: utf-8
"""
@CreateTime: 2022/09/20 12:13
@Author: DJW
@LastEditTime:
@Desctiption:汇一水质数据入网，5分钟上传一次
"""
import ssl
import datetime
import time
import pymysql
import socket
import os
from binascii import *


def conn_mysql(host, user, passwd, db, port=3306):
    """连接MySQL数据库"""
    try:
        conn = pymysql.connect(host=host, user=user, password=passwd, database=db, port=port, autocommit=True)
        return conn
    except Exception as e:
        print(f"[{now_time}]-ERROR [conn_mysql] {e}")
        return False

def select_sql(sql):
    """查询MySQL中的数据"""
    try:
        # conn = conn_mysql(host="127.0.0.1", user="zz", passwd="zzZZ4144670..", db="shucai_huiyi")
        conn = conn_mysql(host="127.0.0.1", user="root", passwd="123456", db="shucai_huiyi")
        if conn:
            cursor = conn.cursor()
            # cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results
    except Exception as e:
        print(f"[{now_time}]-ERROR [select_sql] {e}")
        return False
def update_sql(sql):
    """更新MySQL中的数据"""
    try:
        # conn = conn_mysql(host="127.0.0.1", user="zz", passwd="zzZZ4144670..", db="shucai_huiyi")
        conn = conn_mysql(host="127.0.0.1", user="root", passwd="123456", db="shucai_huiyi")
        if conn:
            cursor = conn.cursor()
            # cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            return True
    except Exception as e:
        print(f"[{now_time}]-ERROR [update_sql] {e}")
        return False

def conn_socket(ip, port, time):
    """创建服务器套接字"""
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许重用本地地址和端口
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
    tcp_sock.settimeout(time)  # 设置超时时间10s
    tcp_sock.connect((ip, port))
    # print(tcp_sock)
    return tcp_sock

def reconn_socket():
    """断线重连"""
    while True:
        try:
            global sock
            sock = conn_socket(upload_ip, upload_port, 10)
            print("reconnect success!")
            break
        except Exception as e:
            print(f"[{now_time}]-ERROR [reconn_socket] {upload_ip}:{upload_port} {e}")
            print("Reconnect in 5 seconds...")
            time.sleep(5)

def send_socket(sock, data):
    """发送数据"""
    # sock = conn_socket(ip, port, 10)
    res_result = False
    if sock:
        try:
            sock.send(bytes.fromhex(data))     # 发送数据，将数据以字节流形式发出
            res_result = True
            print(f"[{now_time}]-SUCCESS [send_socket] \"{data}\"")
        except Exception as e:
            res_result = False
            print(f"[{now_time}]-ERROR [send_socket] \"{data}\" {e}")
    # sock.close()     # 关闭套接字
    return res_result

def get_socket(ip, port, flag):
    """接收数据"""
    if flag == 0:
        sec = 1
    else:
        sec = 2
    sock = conn_socket(ip, port, sec)
    data = False
    if sock:
        try:
            data = sock.recv(1024)     # 接收数据，将数据以字节流形式发出
            time.sleep(0.5)
            print(f"[{now_time}]-SUCCESS [get_socket] getdata: \"{data}\"")
        except Exception as e:
            print(f"[{now_time}]-ERROR [get_socket] {e}")
    sock.close()     # 关闭套接字
    return data


def change_data_status(sql_data_times):
    """更新已入网的数据的状态"""
    try:
        # 更新已上传
        upload_status_sql = f"UPDATE `table_shuizhi` SET is_upload=1 WHERE times<='{sql_data_times}' AND is_upload=0;"
        update_sql(upload_status_sql)
        # 更新包编号
        update_package_num_sql = f"UPDATE `other_data` SET num=num+1 WHERE id=1;"
        update_sql(update_package_num_sql)
        # 更新上次的数据时间
        update_last_time_sql = f"UPDATE `other_data` SET last_time='{sql_data_times}' WHERE id=1;"
        update_sql(update_last_time_sql)

        return True
    except Exception as e:
        print(f"[{now_time}]-ERROR [change_data_status] {e}")
        return False

def crc32Add(read):
    """生成CRC32校验码"""
    data = read.replace(" ", "")    # 消除空格
    read_crc32 = hex(crc32(unhexlify(data)))
    return read+read_crc32[2:]

def get_package_num():
    """获取包编号"""
    # conn = conn_mysql(host="127.0.0.1", user="zz", passwd="zzZZ4144670..", db="shucai_huiyi")
    conn = conn_mysql(host="127.0.0.1", user="root", passwd="123456", db="shucai_huiyi")
    if conn:
        cursor = conn.cursor()
        sql = "SELECT num FROM `other_data`"
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        data = hex(data)[2:]
        result = '0'*(4-len(data)) + data
        cursor.close()
        return result
def update_package_num():
    """检查更新包编号"""
    nowTime = datetime.datetime.now()
    sql_zero_time = select_sql("SELECT zero_time FROM `other_data`")[0][0]
    # 若过0点更新下一天的0点 并将数值置为0
    if nowTime > sql_zero_time:
        next_date = datetime.date.today() + datetime.timedelta(days=1)
        next_zero_time = next_date.strftime("%Y-%m-%d 00:00:00")
        next_zero_time = datetime.datetime.strptime(next_zero_time, "%Y-%m-%d 00:00:00")
        sql = "UPDATE `other_data` " \
              f"SET zero_time = '{next_zero_time}' " \
              "WHERE id = 1"
        update_sql(sql)
        sql = "UPDATE `other_data` " \
              f"SET num = 0 " \
              "WHERE id = 1"
        update_sql(sql)

def get_Data():
    """获取流数据"""
    # get_shuizhi = "SELECT id,times,c2,c1,c3,c7,c4,c5,c6,is_upload FROM `table_shuizhi` WHERE is_upload=0 ORDER BY times LIMIT 1;"
    # get_yelvsu = "SELECT c7,is_upload FROM `table_yelvsu` WHERE is_upload=0 ORDER BY times LIMIT 1;"
    get_shuizhi = "SELECT id,times,c2,c1,c3,c7,c4,c5,c6,is_upload FROM `table_shuizhi` ORDER BY times DESC LIMIT 1;"
    shuizhi = select_sql(get_shuizhi)
    isupload = shuizhi[0][9]
    # print(shuizhi)
    if shuizhi is not False:
        if shuizhi != ():
            shuizhi = list(shuizhi[0])
            if isupload == 0:
                # 获取当前的数据时间
                sql_data_times = shuizhi[1]
                # 保留两位小数
                for i in range(len(shuizhi) - 2):
                    shuizhi[i + 2] = round(shuizhi[i + 2], 2)
                # 转字符串
                shuizhi = [str(i) for i in shuizhi]
                data_str = "{}\t{}\tNAL\tNAL\t{}\t{}\t{}\t{}\t{}\t{}\t{}\tNAL"
                data_str = data_str.format(shuizhi[0], shuizhi[1], shuizhi[2], shuizhi[3], shuizhi[4], shuizhi[5],
                                           shuizhi[6], shuizhi[7], shuizhi[8])
                # print(data_str)
                data_str_hex = ""
                for char in data_str:
                    char_hex = hex(ord(char))[2:]
                    char_hex = char_hex if len(char_hex) == 2 else "0" + char_hex
                    data_str_hex += char_hex

                # 计算包长度
                data_len = hex(int(len(data_str_hex)/2))[2:]
                data_len = '0'*(4-len(data_len)) + data_len     # 补零

                return data_str_hex, data_len, sql_data_times
            else:
                print(f"[{now_time}]-INFO [deal_data] 数据上传过了")
                return False, False, False
        else:
            print(f"[{now_time}]-INFO [deal_data] 读取数据为0")
            return False, False, False
    else:
        print(f"[{now_time}]-ERROR [deal_data] 读取数据失败")
        return False, False, False

def get_unupload_data():
    """获取未上传的数据"""
    SOH = "55aa"                # 开始符
    Site = "02ef"               # 站点编号
    Protocol = "0101"           # 协议
    Byte = "01"                 # 字节序
    Backup = "ffffffff"         # 备用位
    Data, Length, sql_data_times = get_Data()    # 流数据和包长度
    Num = get_package_num()     # 包编号
    TimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')    # 时间戳
    if Data:
        unupload_data = SOH + Site + Protocol + TimeStamp + Num + Length + Byte + Backup + Data
        unupload_data = crc32Add(unupload_data)  # 加上CRC32校验码
        return unupload_data, sql_data_times
    else:
        return False, False


def main(sock):
    # 检查更新包编号
    update_package_num()
    # 获取未上传的数据
    data, sql_data_times = get_unupload_data()
    if data and sql_data_times:
        try:
            # 发送数据
            send_res = send_socket(sock, data)
            # 修改数据的上传状态
            if send_res:
                if change_data_status(sql_data_times):
                    print(f"[{now_time}]-SUCCESS [main] 发送成功")
        except Exception as e:
            print(f"[{now_time}]-ERROR [main] {e}")

if __name__ == '__main__':
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # upload_ip = "223.78.117.245"
    # upload_port = 8004
    global sock
    upload_ip = "192.168.2.200"
    upload_port = 4001
    try:
        sock = conn_socket(upload_ip, upload_port, 10)
        print("connect success!")
    except Exception as e:
        print(f"[{now_time}]-ERROR [conn_socket] {upload_ip}:{upload_port} {e}")
        reconn_socket()

    while True:
        main(sock)
        time.sleep(5)

