from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys
import pandas as pd

address = "192.168.0.54"
# 토큰 받아오기
class AccountView():
    def token(self):
        # data2 = json.loads(request.body)
        # Admin으로 Token 발급 Body
        token_payload = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": "admin",
                            "domain": {
                                "name": "Default"
                            },
                            "password": "0000"
                        }
                    }
                }
            }
        }  

        # Openstack keystone token 발급
        auth_res = requests.post("http://"+address+"/identity/v3/auth/tokens",
            headers = {'content-type' : 'application/json'},
            data = json.dumps(token_payload))

        #발급받은 token 출력
        admin_token = auth_res.headers["X-Subject-Token"]
        print("token",admin_token)
        return admin_token


    def create_stack(self):
        admin_token= self.token()
        system_num=int(input("원하는 시스템 번호를 입력: 1.강의시스템 2.웹서버 \n"))
        memberFile=pd.read_csv('test_csv_file.csv')
        for i in range(memberFile.shape[0]):
            id, name, passwd = memberFile.loc[i]
        softInfo=['vim','filezilla','ftp','default-jdk','synaptic']
        softNum = list(map(int, input("원하는 소프트웨어 번호를 입력: 1.vim 2.filezilla 3.ftp 4.default-jdk 5.synaptic  입력예시: 1 3 4\n").split()))

        # stack_name= input("stack 이름 입력 : ")
        # key_name= input("key 이름 입력 : ")
        # server_name= input("server 이름 입력 : ") 
        # num_user=int(input("사용자 수 입력: ")) 
        osList=['ubuntu.json','centos']
        # with open(osList[system_num-1], 'w') as f:
        #     json_data = json.load(f)
        # print(osList[system_num-1])
        with open('ubuntu.json', 'r') as f:
            json_data = json.load(f)
        for i in softNum:
            json_data['template']['resources']['myconfig']['properties']['cloud_config']['packages'].append(softInfo[i - 1])
        print(json_data['template']['resources']['myconfig']['properties']['cloud_config']['packages'])

        # if(system_num==1):
        #     with open('ubuntu.json','r') as f:
        #         json_data=json.load(f)
        # elif(system_num==2):
        #     with open('centos.json','r') as f:
        #         json_data=json.load(f)
        # elif(system_num==3):
        #     with open('fedora-0223.json','r') as f:
        #         json_data=json.load(f)
        # json_data['stack_name']=stack_name
        # json_data['template']['resources']['demo_key']['properties']['name']=key_name
        # json_data['template']['resources']['mybox']['properties']['name']=server_name
        # for i in range(num_user):
        #     json_data['template']['resources']['myconfig']['properties']['cloud_config']['users'].append("%d"%(i))
        #     json_data['template']['resources']['myconfig']['properties']['cloud_config']['chpasswd']["list"].append("%d:%d%d%d%d"%(i,i,i,i,i))

            
        user_res = requests.post("http://"+address+"/heat-api/v1/6afe05fbd2cb47a6b149ee3541fb47a6/stacks",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        print("stack생성 ",user_res)


def main():
    f=AccountView()
    f.create_stack()


main()