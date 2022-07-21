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
        start = time.time()
        admin_token= self.token()
        system_num=int(input("원하는 OS 번호를 입력: 1.Ubuntu 2.CentOS 3.Fedora\n"))
        SW_num=int(input("원하는 SW 번호를 입력: 1.node.js 2.ML_Model \n"))
        Data_num=int(input("원하는 Data 번호를 입력: 1.Dataset_ML 2.Data_State \n"))

        system=[["","ba2211d6-33e6-4bc4-af3f-c03d28727f17"],["",""],["",""]]
        Data=["9409d40a-e4e0-491b-8a6e-baa36894cbe9",""]

        OS_SW_id=system[system_num-1][SW_num-1]
        data_id=Data[Data_num-1]
        

        with open('patent_volume_snapshot.json','r') as f:
            json_data=json.load(f)
        json_data['snapshot']['volume_id']=OS_SW_id
        # print(json_data)

        json_DataPool=copy.deepcopy(json_data)
        json_DataPool['snapshot']['volume_id']=data_id
        #볼륨 -> 스냅샷 생성

        # 1. OS_SW snapshot
        user_res_OS_SW = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/snapshots",
            headers = {'Content-Type': 'application/json', 'X-Auth-Token' : admin_token},
            data = json.dumps(json_data))
        snap_uuid=user_res_OS_SW.json()['snapshot']['id']

        # 2. DataPool snapshot
        user_res_DataPool = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/snapshots",
            headers = {'Content-Type': 'application/json', 'X-Auth-Token' : admin_token},
            data = json.dumps(json_DataPool))
        snap_uuid_datapool=user_res_DataPool.json()['snapshot']['id']

        print("OS_SW 스냅샷 생성 : ",user_res_OS_SW)
        print("데이터풀 스냅샷 생성 : ",user_res_DataPool)
        # print("Snapshot 아이디 : ", snap_uuid, "and datapool id",snap_uuid_datapool)

        #스냅샷 -> 볼륨 json file load
        with open('patent_volume.json','r') as f:
            json_data_vol=json.load(f)
        # print(json_data_vol)  

        json_data_vol['volume']['snapshot_id']=snap_uuid

        json_data_vol_data=copy.deepcopy(json_data_vol)
        json_data_vol_data['volume']['snapshot_id']=snap_uuid_datapool

        # Wait until snapshot status available
        while True :
            snap_status=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/snapshots?id="+snap_uuid,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['snapshots'][0]['status']
            snap_status_data=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/snapshots?id="+snap_uuid_datapool,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['snapshots'][0]['status']
            # print("SnapShot status : ",snap_status, snap_status_data)
            if snap_status=="available" and snap_status_data=="available": break
            else : 
                if snap_status=="error" or snap_status_data=="error":
                    print("snapshot status is error. terminate process.")
                    return 0
                else: 
                    # print("snapshot status is : ",snap_status)
                    sleep(0.5)

        # Create Volume
        user_res1 = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/volumes",
            headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token},
            data = json.dumps(json_data_vol))
        print("OS_SW Volume 생성 : ",user_res1)
        Volume_snap_uuid=user_res1.json()['volume']['id']


        user_res1_data = requests.post("http://"+address+"/volume/v3/"+tenet_id+"/volumes",
            headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token},
            data = json.dumps(json_data_vol_data))
        print("데이터풀 Volume생성 : ",user_res1_data)
        Volume_snap_uuid_data=user_res1_data.json()['volume']['id']
        
        
        # Wait until Volume status available
        while True :
            volume_status=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/volumes/detail?id="+Volume_snap_uuid,
                headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token}).json()['volumes'][0]['status']
            volume_status_data=requests.get("http://"+address+"/volume/v3/"+tenet_id+"/volumes/detail?id="+Volume_snap_uuid_data,
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


        # Create Instance Payload
        with open('patent_block_device.json','r') as f:
            json_data_block=json.load(f)
        json_data_block['uuid']=Volume_snap_uuid
        # print(json_data_block)
        
        json_data_block_Datapool = copy.deepcopy(json_data_block)
        json_data_block_Datapool["uuid"]=Volume_snap_uuid_data
        json_data_block_Datapool["boot_index"]=1
        with open('patent_payload.json','r') as f:
            json_data_VM=json.load(f)
        json_data_VM['server']['block_device_mapping_v2'].append(json_data_block)
        json_data_VM['server']['block_device_mapping_v2'].append(json_data_block_Datapool)
        # print("payload is \n",json_data_VM)

        # Create Instance
        res_instance = requests.post("http://"+address+"/compute/v2.1/servers",
            headers = {'Content-Type': 'application/json','X-Auth-Token' : admin_token},
            data = json.dumps(json_data_VM))
        print("Instance 생성 : ",res_instance)
        end = time.time()
        print("제안 시스템의 가상환경 구축 시간 : ", end-start)
def main():
    f=AccountView()
    # f.create_snapshot_image()
    f.create_server_from_volume()

main()
