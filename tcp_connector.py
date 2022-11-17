"""
@Date  :2021/5/21/00219:10:57
@Desc  :tcp socket连接类
"""
import time
import socket


class TcpConnector:
    def __init__(self, ip, port):
        self.__sock = None
        self.__connected = False
        self.__size = 1024
        self.__ip = ip
        self.__port = port
        self.__last_save_time = 0
        self.__connect()

    # 建立socket连接
    def __connect(self):
        if self.__sock:
            self.__sock.close()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许重用本地地址和端口
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
        self.__sock.settimeout(10)  # 设置超时时间3mins
        try:
            self.__sock.connect((self.__ip, self.__port))
            print(f'Connect to [{self.__ip}]:[{self.__port}] success !')
            self.__connected = True
        except Exception as e:
            print(f'Connect to [{self.__ip}]:[{self.__port}] failed:{e} !!!')
            self.__connected = False
            self.__reconnect()

    def __reconnect(self):
        while True:
            try:
                if self.__sock:
                    self.__sock.close()
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
                self.__sock.settimeout(180)  # 设置超时时间3mins
                self.__sock.connect((self.__ip, self.__port))
                self.__connected = True
                print(f'Reconnect to [{self.__ip}]:[{self.__port}] success !')
                break
            except Exception as e:
                print(f'Reconnect to [{self.__ip}]:[{self.__port}] failed:{e} !!! Continue reconnect in 5s..')
                self.__connected = False
                time.sleep(5)

    def close(self):
        """Close the connection with the TCP Slave"""
        if self.__sock:
            self.__sock.close()
            self.__sock = None
            self.__connected = False

    def send_command(self, data):
        if self.__sock:
            try:
                send_data = bytes.fromhex(data)
                self.__sock.send(send_data)
                return True
                # self.__sock.send(data.encode(encoding='utf-8'))
            except Exception as e:
                print(f'Send command to [{self.__ip}]:[{self.__port}] error:{e}')
                self.__reconnect()
                return False

    def exec_command(self, data):
        try:
            send_data = bytes.fromhex(data)
            # com = command['instruct'].encode(encodings='utf-8')
            self.__sock.send(send_data)
            recv_data = self.__sock.recv(self.__size)
            return recv_data
        except Exception as e:
            print(f"{e}")

