import socket
import os ,sys
import threading as th
from time import sleep
from os.path import exists

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

def getMsg(client_socket, addr) :
    data = str()
    msg = client_socket.recv(1024)
    while msg :
        data += msg.decode('utf-8')
        msg = client_socket.recv(1024)
    return data

def doSomething(client_socket, addr) :
    request_type = getMsg(client_socket, addr)
    if(request_type == "reset") :
        logReset()
    elif(request_type == "result") :
        XXEResult(client_socket)

if __name__ == "__main__" : 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    while True :
        try :
            client_socket, addr = server_socket.accept()
            print("new client Connected : {}\n".format(addr))
        except socket.error as err:
            client_socket.close()
            print("Disconnected : {}, {}\n".format(addr, err))
        except KeyboardInterrupt as key :
            client_socket.close()
            server_socket.close()
        do = th.Thread(doSomething, args=(client_socket, addr))
        do.daemon = True
        do.start()