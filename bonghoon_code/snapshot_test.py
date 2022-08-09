from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys
import pandas as pd

address = "192.168.0.81"
server_id = "15412a03-53ea-4f3b-8139-5199e7909381"
public_ip ="4a1e754d-590f-4473-a8e7-dc230021007d"


snap_image_id="4eef465c-7ab8-4acf-9ea6-12ee5b5af30f"
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

    def create_snapshot_image(self):
        admin_token= self.token()
        image_name= input("이미지 이름을 입력: \n")
        json_data = {
            "createImage" : {
                "name" : image_name
            }
        }
        user_res = requests.post("http://"+address+"/compute/v2.1/servers/"+server_id+"/action",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        print("snapshot 생성 ",user_res)
    


    def create_snap_instance(self):
        admin_token= self.token()
        json_data ={
            
            "server" : {
                "name" : "snapshot_api_test",
                "imageRef" : snap_image_id,
                "networks" : [{
                    "uuid" : public_ip,
                }],
                "flavorRef" : "d1",
                "security_groups": [
                    {
                        "name": "default"
                    }
                ]
            }
        }
        user_res = requests.post("http://"+address+"/compute/v2.1/servers",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        print("instance 생성 ",user_res)

def main():
    f=AccountView()
    # f.create_snapshot_image()
    f.create_snap_instance()

main()