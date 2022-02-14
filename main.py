from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys

address = "10.125.70.26"
# 토큰 받아오기
class AccountView():
    def token():
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


    def create_stack():
        admin_token= AccountView.token()
        system_num=int(input("원하는 시스템 번호를 입력: 1.Ubuntu 2.CentOS 3.Fedora"))
        stack_name= input("stack 이름 입력 : ")
        key_name= input("key 이름 입력 : ")
        server_name= input("server 이름 입력 : ") 
        num_user=int(input("사용자 수 입력: ")) 
        with open('main.json','r') as f:
            json_data=json.load(f)
        if(system_num==1):
            json_data['template']['resources']['mybox']['properties']['image']="ubuntu"
        elif(system_num==2):
            json_data['template']['resources']['mybox']['properties']['image']="centos"
        elif(system_num==3):
            json_data['template']['resources']['mybox']['properties']['image']="Fedora-Cloud-Base-33-1.2.x86_64"
        json_data['stack_name']=stack_name
        json_data['template']['resources']['demo_key']['properties']['name']=key_name
        json_data['template']['resources']['mybox']['properties']['name']=server_name
        for i in range(num_user):
            json_data['template']['resources']['myconfig']['properties']['cloud_config']['users'].append("%d"%i)
            json_data['template']['resources']['myconfig']['properties']['cloud_config']['chpasswd']["list"].append("%d:%d%d%d%d"%(i,i,i,i,i))
        user_res = requests.post("http://"+address+"/heat-api/v1/6afe05fbd2cb47a6b149ee3541fb47a6/stacks",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        print("stack생성 ",user_res)

def main():
     f=AccountView.create_stack()


main()