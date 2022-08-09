from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys
import pandas as pd

address = "192.168.0.81"
tenet_id = "befce16c8c784857acbb4ae98ec7af45"
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


    def split(self):
        admin_token= self.token()
        system_num=int(input("원하는 시스템 번호를 입력: 1.Ubuntu 2.CentOS 3.Fedora\n"))
        # stack_name= input("stack 이름 입력 : ")
        # key_name= input("key 이름 입력 : ")
        # server_name=1 input("server 이름 입력 : ") 
        # num_user=int(input("사용자 수 입력: ")) 

        if(system_num==1):
            with open('main.json','r') as f:
                json_data=json.load(f)
        elif(system_num==2):
            with open('centos.json','r') as f:
                json_data=json.load(f)
        elif(system_num==3):
            with open('fedora-0223.json','r') as f:
                json_data=json.load(f)
        # json_data['stack_name']=stack_name
        # json_data['template']['resources']['demo_key']['properties']['name']=key_name
        # json_data['template']['resources']['mybox']['properties']['name']=server_name
        # for i in range(num_user):
        #     json_data['template']['resources']['myconfig']['properties']['cloud_config']['users'].append("%d"%(i))
        #     json_data['template']['resources']['myconfig']['properties']['cloud_config']['chpasswd']["list"].append("%d:%d%d%d%d"%(i,i,i,i,i))
        
            #address heat-api v1 프로젝트 id stacks
        user_res = requests.post("http://"+address+"/heat-api/v1/"+tenet_id+"/stacks",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        print("stack생성 ",user_res)


def main():

    with open('main.json','r') as f:
        json_data=json.load(f)
    del(json_data['stack_name'])
    with open('split_result.json','w') as t:
        json.dump(json_data,t,indent='\t')

main()