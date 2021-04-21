import socket
import os ,sys
from time import sleep
from os.path import exists
from _thread import *

# 소켓 연결할때 서버쪽에서는 자신의 로컬 ip를 적어주더라구요 ..
HOST = '192.168.200.146'
PORT = 62162
filename = "/var/log/apache2/access.log"

def logReset() :
    os.system("echo "" > {}".format(filename))

def XXEResult(client_socket) :
    data_transferred = 0
    if not exists(filename) :
        print("Files does not exist\n")
    else :
        with open(filename, 'rb') as f:
            try:
                data = f.read(1024)
                while data:
                    data_transferred += client_socket.send(data)
                    data = f.read(1024)
            except Exception as ex:
                print(ex)
        print("\n [complete] \n -- %d"%data_transferred, " byte")

def getMsg(client_socket) :
    data = str()
    msg = client_socket.recv(1024)
    while msg :
        data += msg.decode('utf-8')
        msg = client_socket.recv(1024)
    return data

def doSomething(client_socket, addr) :
    while True :
        try :
            request_type = getMsg(client_socket)
            if(request_type == "reset") :
                logReset()
            elif(request_type == "result") :
                XXEResult(client_socket)
        except ConnectionResetError as e :
                print('Disconnected by ' + addr[0],':',addr[1])
                break
    client_socket.close()

if __name__ == "__main__" : 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    while True :
        try :
            client_socket, addr = server_socket.accept()
            print("new client Connected : {}\n".format(addr))
            start_new_thread(doSomething, (client_socket, addr))
        except socket.error as err:
            client_socket.close()
            print("Disconnected : {}, {}\n".format(addr, err))
        except KeyboardInterrupt as key :
            server_socket.close()