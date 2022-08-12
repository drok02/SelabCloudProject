from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys
import pandas as pd
from time import sleep
import copy
import time
address = "192.168.0.118"
tenet_id = "91d317f465b84ed2bc9f123eac5f8b07"
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

    def create_server_from_volume(self):
        # start = time.time()
        admin_token= self.token()
        system_num=int(input("원하는 OS 번호를 입력: 1.Ubuntu 2.CentOS 3.Fedora\n"))
        SW_num=int(input("원하는 SW 번호를 입력: 1.node.js 2.ML_Model \n"))
        Data_num=int(input("원하는 Data 번호를 입력: 1.Dataset_ML 2.Data_State \n"))

        system=[["68e4e1ba-56f4-4b72-9527-013fbc32fe37","ba2211d6-33e6-4bc4-af3f-c03d28727f17"],["5a0ed308-cefa-4629-8abf-dac148f32917",""],["44f02b28-a88c-4544-b0ec-7a86192828ec","4f2426ca-7eaa-4582-9df6-30eb019cea0f"]]
        Data=["9409d40a-e4e0-491b-8a6e-baa36894cbe9","2aec7fc6-3929-4a51-b326-34aaedd2cc3a"]

        OS_SW_id=system[system_num-1][SW_num-1]
        data_id=Data[Data_num-1]
        
        # 스냅샷 템플릿 생성
        with open('patent_volume_snapshot.json','r') as f:
            json_data=json.load(f)

        # OS_SW 리소스 스냅샷 템플릿 작성
        json_data['snapshot']['volume_id']=OS_SW_id
        # Data 리소스 스냅샷 템플릿 작성
        json_DataPool=copy.deepcopy(json_data)
        json_DataPool['snapshot']['volume_id']=data_id
       
        # 볼륨 -> 스냅샷 생성

        # SW 리소스의 snapshot 생성
        user_snap_OS_SW = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/snapshots",
            headers = {'Content-Type': 'application/json', 'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        snap_uuid=user_snap_OS_SW.json()['snapshot']['id']

        # DataPool 리소스의 snapshot 생성
        user_snap_DataPool = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/snapshots",
            headers = {'Content-Type': 'application/json', 'X-Auth-Token' : admin_token},
            data = json.dumps(json_DataPool))
        snap_uuid_datapool=user_snap_DataPool.json()['snapshot']['id']

        # Wait until snapshot status available
        while True :
            snap_status=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/snapshots?id="+snap_uuid,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['snapshots'][0]['status']
            snap_status_data=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/snapshots?id="+snap_uuid_datapool,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['snapshots'][0]['status']
            if snap_status=="available" and snap_status_data=="available": break
            else : 
                if snap_status=="error" or snap_status_data=="error":
                    print("snapshot status is error. terminate process.")
                    return 0
                else: 
                    sleep(0.5)

        # 스냅샷의 볼륨 템플릿 생성
        with open('patent_volume.json','r') as f:
            json_data_vol=json.load(f)

        # OS_SW 볼륨 템플릿 작성
        json_data_vol['volume']['snapshot_id']=snap_uuid
        # Datapool 볼륨 템플릿 작성
        json_data_vol_data=copy.deepcopy(json_data_vol)
        json_data_vol_data['volume']['snapshot_id']=snap_uuid_datapool
        # 생성 요청
        user_vol_OSSW = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/volumes",
            headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token},
            data = json.dumps(json_data_vol))
        Volume_uuid_sw=user_vol_OSSW.json()['volume']['id']

        user_vol_data = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/volumes",
            headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token},
            data = json.dumps(json_data_vol_data))
        Volume_uuid_data=user_vol_data.json()['volume']['id']
    
        # Wait until Volume status available
        while True :
            volume_status=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/volumes/detail?id="+Volume_uuid_sw,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['volumes'][0]['status']
            volume_status_data=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/volumes/detail?id="+Volume_uuid_data,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['volumes'][0]['status']
            # print("SnapShot status : ",volume_status, volume_status_data)
            if volume_status=="available" and volume_status_data=="available": break
            else : 
                if volume_status=="error" or volume_status_data=="error":
                    print("volume status is error. terminate process.")
                    return 0
                else: 
                    # print("volume status is : ",volume_status)
                    sleep(0.5)


        # 가상환경_Volume 항목 템플릿 생성
        with open('patent_block_device.json','r') as f:
            json_data_block=json.load(f)

        # OS_SW Volume 템플릿 작성
        json_data_block['uuid']=Volume_uuid_sw

        # DataPool 템플릿 작성
        json_data_block_Datapool = copy.deepcopy(json_data_block)
        json_data_block_Datapool["uuid"]=Volume_uuid_data
        json_data_block_Datapool["boot_index"]=1

        # 가상환경 Create 템플릿 생성      
        with open('patent_payload.json','r') as f:
            json_data_VM=json.load(f)
        # OS_SW,DataPool Volume 추가
        json_data_VM['server']['block_device_mapping_v2'].append(json_data_block)
        json_data_VM['server']['block_device_mapping_v2'].append(json_data_block_Datapool)

        # Create 가상환경
        res_instance = requests.post("http://"+address+"/compute/v2.1/servers",
            headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token},
            data = json.dumps(json_data_VM))

        res_instance
def main():
    f=AccountView()
    f.create_server_from_volume()

main()
