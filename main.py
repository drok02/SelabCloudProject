from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys
import pandas as pd
import time
address = "192.168.0.118"
tenet_id = "91d317f465b84ed2bc9f123eac5f8b07"
# 토큰 받아오기
class AccountView():
    def Request(self,apiURL, jsonData):
        auth_res = requests.post("http://"+address+apiURL,
            headers = {'content-type' : 'application/json'},
            data = json.dumps(jsonData))
        return auth_res

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
        # auth_res = requests.post("http://"+address+"/identity/v3/auth/tokens",
        #     headers = {'content-type' : 'application/json'},
        #     data = json.dumps(token_payload))
        url="/identity/v3/auth/tokens"
        auth_res=self.Request(url,token_payload)
        #발급받은 token 출력
        admin_token = auth_res.headers["X-Subject-Token"]
        print("token : \n",admin_token)
        return admin_token


    def create_stack(self):
        
        start = time.time()
        admin_token= self.token()
        system_num=int(input("원하는 시스템 입력: 1.Ubuntu 2.CentOS 3.Fedora\n"))
        stack_name= int(input("Flavor 선택 : 1. m1.nano 2. m1.small 3. m1.medium 4. m1.large\n"))
        key_name= int(input("네트워크 입력 : 1. public 2. private 3. shared\n"))
        server_name=int(input("SW 입력 : 1. apache2 2. pwgen 3. libguestfs-tools 4. pastebinit\n")) 

        if(system_num==1):
            with open('main.json','r') as f:
                json_data=json.load(f)
        elif(system_num==2):
            with open('centos.json','r') as f:
                json_data=json.load(f)
        elif(system_num==3):
            with open('fedora-0223.json','r') as f:
                json_data=json.load(f)
     
            #address heat-api v1 프로젝트 id stacks
        user_res = requests.post("http://"+address+"/heat-api/v1/"+tenet_id+"/stacks",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        print("stack생성 ",user_res)
        end = time.time()
        print("종래 시스템의 오케스트레이션 가상환경 생성 시간 : ", end-start)

def main():
    f=AccountView()
    f.create_stack()


main()