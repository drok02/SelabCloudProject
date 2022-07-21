from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys
import pandas as pd
# memberFile=pd.read_csv('test_csv_file.csv')
#         for i in range(memberFile.shape[0]):
#             id, name, passwd = memberFile.loc[i]
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
        #API 요청을 위한 인증 토큰 발급
        admin_token= self.token()

        #사용자 요구사항중 OS 입력
        osList=['ubuntu.json','centos.json','fedora.json']
        system_num=int(input("원하는 OS 번호를 입력: 1.Ubuntu 2.CentOS 3.Fedora \n"))

        #사용자 요구사항중 SW 입력
        softInfo = ['vim','filezilla','ftp','default-jdk','synaptic']
        softNum = list(map(int, input("원하는 소프트웨어 번호를 입력: 1.vim 2.filezilla 3.ftp 4.default-jdk 5.synaptic  입력예시: 1 3 4\n").split()))
        
        #기본 템플릿 생성
        with open(osList[system_num-1], 'r') as f:
            json_data = json.load(f)
        
        #기본 템플릿 항목에 요구사항 입력
        for i in softNum:
            json_data['template']['resources']['myconfig']['properties']['cloud_config']['packages'].append(softInfo[i - 1])
        print(json_data['template']['resources']['myconfig']['properties']['cloud_config']['packages'])

        #클라우드 플랫폼 오케스트레이션 요청
        user_res = requests.post("http://"+address+"/heat-api/v1/6afe05fbd2cb47a6b149ee3541fb47a6/stacks",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        
        #맞춤형 가상머신 생성 결과 출력
        print("stack생성 ",user_res)


def main():
    f=AccountView()
    f.create_stack()


main()