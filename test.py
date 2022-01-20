from django.shortcuts import render
import json
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
address = "164.125.70.22"
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

    def create_user():
        #openstack 사용자 생성
        admin_token= AccountView.token()
        # 사용자의 openstack 정보 

        #프로젝트 id 참조
        default_project_id= requests.get("http://"+address+"/identity/v3/projects?name=admin",
        headers = {'X-Auth-Token' : admin_token}).json()
        default_project_id=default_project_id["projects"][0]["id"]

        #admin 그룹 id 참조
        group_id= requests.get("http://"+address+"/identity/v3/groups?name=admins",
        headers = {'X-Auth-Token' : admin_token}).json()["groups"][0]["id"]
        

        #admin role id 참조
        role_id= requests.get("http://"+address+"/identity/v3/roles?name=admin",
        headers = {'X-Auth-Token' : admin_token}).json()["roles"][0]["id"]
        username= input("생성할 사용자 이름 입력 : ")
        
        openstack_uesr_payload = {
            "user": {
                "name": username,
                "password": '0000',
                "default_project_id": default_project_id
            }
        }

        #사용자 정보 참조
        user_res = requests.post("http://"+address+"/identity/v3/users",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_uesr_payload))

        print("생성된 사용자 이름은 :",openstack_uesr_payload["user"]["name"])

        #openstack id 확인
        # 생성된 사용자를 admins 그룹에 추가, admin 역할에 추가

        openstack_id = user_res.json()["user"]["id"]
        group_res = requests.put("http://"+address+"/identity/v3/groups/"+group_id+"/users/"+ openstack_id,
            headers = {'X-Auth-Token' : admin_token})

        permission_req = requests.put("http://"+address+"/identity/v3/domains/default/users/"+openstack_id+"/roles/"+role_id)



        # response = JsonResponse(openstack_uesr_payload,status = 200)
        # response['Access-Control-Allow-Origin'] ='*'
        # return response

        return openstack_uesr_payload["user"]["name"]


    def delete_user():
        admin_token= AccountView.token()
        username=input("삭제할 사용자 이름 입력: ")
        user_res= requests.get("http://"+address+"/identity/v3/users?name="+username,
            headers = {'X-Auth-Token' : admin_token})
        user_id=user_res.json()
        user_detail=user_id["users"][0]["id"]    
        
        print(user_detail) 
        
        user_res = requests.delete("http://"+address+"/identity/v3/users/{id}".format(id=user_detail),
            headers = {'X-Auth-Token' : admin_token}
            )
        print("사용자 삭제 완료")
        # openstack_id = user_res.json()["user"]["id"]
        # group_res = requests.put("http://"+address+"/identity/v3/groups/65d8b8f223c249dbb5c316b3c604bea2/users/"+ openstack_id,
        #     headers = {'X-Auth-Token' : admin_token})

        # permission_req = requests.put("http://"+address+"/identity/v3/domains/default/users/"+openstack_id+"/roles/a72b87b6428c4a568b4116b2a500da9b")
        # response = JsonResponse(data2,status = 200)
        # response['Access-Control-Allow-Origin'] ='*'
        # return response
    def signin():
        admin_token= AccountView.token()
    

    #인스턴스 생성 
    def create_instance():
        admin_token= AccountView.token()
        instacne_name=input("생성할 인스턴스 이름 입력: ")
        # 특정 (shared) 네트워크 참조
        network_uuid = requests.get("http://"+address+":9696/v2.0/networks?name=shared",
            headers = {'X-Auth-Token' : admin_token}
            ).json()["networks"][0]["id"]
        print()
        print("network uuid : "+network_uuid)
        print()

        #특정 img id 참조
        img_uuid = requests.get("http://"+address+"/image/v2/images?name=cirros-0.4.0-x86_64-disk",
            headers = {'X-Auth-Token' : admin_token}
            ).json()["images"][0]["id"]

        flavor_reference= input("flavor ref id 입력: ")
        openstack_instance_payload = {
            "server" : {
                "name" : instacne_name,
                "imageRef" : img_uuid,
                "flavorRef" : flavor_reference,
                "networks" : [{
                    "uuid" : network_uuid
                }] 
            }   
        }
        #인스턴스 생성 요청
        user_res = requests.post("http://"+address+"/compute/v2.1/servers",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_instance_payload))
        print(user_res.json())


    #인스턴스로부터 스냅샷 이미지 생성
    def create_img_from_server():
        admin_token= AccountView.token()
        instacne_name=input("참고할 인스턴스 이름 입력: ")
        img_name=input("생성할 이미지 이름 입력 :")
        instance_uuid=requests.get("http://"+address+"/compute/v2.1/servers/detail?"+instacne_name,
            headers = {'X-Auth-Token' : admin_token}
            ).json()["servers"][0]["id"]

        openstack_img_payload = {
                "createImage" : {
                    "name" : img_name
                }     
        }
        #인스턴스 바탕으로 이미지 생성
        user_res = requests.post("http://"+address+"/compute/v2.1/servers/"+instance_uuid+"/action",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_img_payload))
        print("인스턴스로부터 이미지 생성 ",user_res)



    # 스냅샷 생성
    def create_snapshot():
        admin_token= AccountView.token()
        snp_name= input("스냅샷 이름 입력 : ")

        openstack_snp_payload = {
            "snapshot": {
                "display_name": snp_name,
                "display_description": "Daily backup",
                "volume_id": "adc9a8ac-168e-4da3-af50-62f247c6b2ca"
            } 
        }
        user_res = requests.post("http://"+address+"/compute/v2.1/os-snapshots",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_snp_payload)).json()
        print("스냅샷 생성 ",user_res)


    #볼륨 생성
    def create_vol():
        admin_token= AccountView.token()
        vol_name= input("볼륨 이름 입력 : ")

        openstack_vol_payload = {
            "volume": {
                "display_name": vol_name,
                "display_description": "Volume Description",
                "size": 100
            }
        }

        user_res = requests.post("http://"+address+"/compute/v2.1/os-volumes",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_vol_payload)).json() 
        print("볼륨생성 ",user_res)

    #flavor 생성    
    def create_flavor():
        admin_token= AccountView.token()
        vol_name= input("flavor 이름 입력 : ")
        flavor_id=input("flavor id 입력: ")
        openstack_fla_payload = {
            "flavor": {
                "name": vol_name,
                "ram": 1024,
                "vcpus": 2,
                "disk": 10,
                "id": flavor_id,
                "rxtx_factor": 2.0,
                "description": "test description"
            }
        }

        user_res = requests.post("http://"+address+"/compute/v2/flavors",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_fla_payload)).json() 
        print("flavor생성 ",user_res)
    def create_stack():
        admin_token= AccountView.token()
        stack_name= input("stack 이름 입력 : ")
        openstack_stack_payload = {
            {
                "files": {},
                "disable_rollback": true,
                "parameters": {
                    "flavor": "m1.tiny",
                    "demo_net_cidr": "10.10.30.0/24",
                    "demo_net_gateway": "10.10.30.1",
                    "demo_net_pool_end" : "10.10.30.200",
                    "demo_net_pool_start" : "10.10.30.10",
                    "image_name": "cirros-0.5.2-x86_64-disk",
                    "key_name":"test-bong",
                    "net_name":"poc-net",
                    "server_name":"heat01",
                    "zone_server":"nova"
                        },
                "stack_name": stack_name,
                "template": {
                    "heat_template_version": "2013-05-23",
                    "description": "Simple template to test heat commands",
                    "parameters": {
                        "flavor": {
                            "default": "m1.tiny",
                            "type": "string"
                        },
                    "demo_net_cidr": {"type": "string"},
                    "demo_net_gateway": {"type": "string"},
                    "demo_net_pool_end" : {"type": "string"},
                    "demo_net_pool_start" : {"type": "string"},
                    "image_name": {"type": "string"},
                    "key_name": {"type": "string"},
                    "net_name": {"type": "string"},
                    "server_name": {"type": "string"},
                    "zone_server": {"type": "string"}
                    },
                    "resources": {
                        "demo_key" : {
                            "type": "OS::Nova::KeyPair",
                            "properties": {
                                "name":
                                    {"get_param" : "key_name"}
                            }
                        },
                        "demo_net":{
                            "properties":{
                            "name":{
                                    "get_param": "net_name"
                            }},
                            "type": "OS::Neutron::Net"
                        },
                        "demo_subnet": {
                            "properties":{
                                "allocation_pools":[{
                                    "start":{"get_param": "demo_net_pool_start"},
                                    "end":{"get_param": "demo_net_pool_end"}
                                }],
                                "cidr": {
                                    "get_param": "demo_net_cidr"},
                                "gateway_ip":{
                                    "get_param": "demo_net_gateway"},
                                "network_id":{"get_resource": "demo_net"}
                            },
                            "type": "OS::Neutron::Subnet"
                        },
                        
                        "server_port":{
                            "properties":{ 
                                "fixed_ips":[{ 
                                    "subnet_id":{"get_resource": "demo_subnet"}}],
                                    
                                "network_id":{"get_resource": "demo_net"}
                                    
                            },                   
                            "type": "OS::Neutron::Port"
                        },

                        "hello_world":{
                            "type": "OS::Nova::Server",
                            "properties":{
                                "availability_zone":{ "get_param": "zone_server"}, 
                                "flavor":{"get_param": "flavor"},
                                "image":{"get_param": "image_name"},
                                "key_name":{"get_resource": "demo_key"},
                                "name":{"get_param": "server_name"},                        
                                "networks": [{"port":{"get_resource": "server_port"}
                                }]
                                }
                            
                        }
                            
                    }
                },
                "timeout_mins": 60
            }
        }
def main():
    # d= AccountView.token()
    # c=AccountView.create_user()
    # f= AccountView.delete_user()
    #f=AccountView.create_instance()
    # f=AccountView.create_img_from_server()
    # f=AccountView.create_snapshot()
    # f=AccountView.create_vol()
    # f=AccountView.create_flavor()


main()
#         #openstack 사용자 생성
#         user_res = requests.token("http://"+address+"/identity/v3/users",
#             headers = {'X-Auth-Token' : admin_token},
#             data = json.dumps(openstack_uesr_payload))
#         print(user_res.json())

#         #openstack id 확인
#         # 생성된 사용자를 admins 그룹에 추가

#         openstack_id = user_res.json()["user"]["id"]
#         group_res = requests.put("http://"+address+"/identity/v3/groups/65d8b8f223c249dbb5c316b3c604bea2/users/"+ openstack_id,
#             headers = {'X-Auth-Token' : admin_token})

#         permission_req = requests.put("http://"+address+"/identity/v3/domains/default/users/"+openstack_id+"/roles/a72b87b6428c4a568b4116b2a500da9b")
#         response = JsonResponse(data2,status = 200)
#         response['Access-Control-Allow-Origin'] ='*'
#         return response

#     def get(self, request):
#         Account_data = Account_info.objects.values()
#         return JsonResponse({'accounts' : list(Account_data)}, status = 200)

#     def delete(self,request):
#         Account_data = Account_info.objects.all()
#         Account_data.delete()
#         return HttpResponse("Delete Success")


# # 로그인
# class SignView(View):
#     def token(self, request):
#         data = json.loads(request.body)
#         # 사용자의 openstack 정보 
#         try:
#             if Account_info.objects.filter(name = data['name']).exists():
#                 user = Account_info.objects.get(name=data['name'])
#                 if user.password == data['password']:
#                     token_payload = {
#                         "name": user.name,
#                         "password": str(user.password),
#                         "project_id": "306a781cdcfe4bb7ae7ff1f8bbba6596"
#                     }                  
#                     # Openstack keystone token 발급
#                     auth_res2 = requests.token("http://52.78.82.160:7014/token",
#                         headers = {'content-type' : 'application/json'},
#                         data = json.dumps(token_payload))
#                     token = auth_res2.json()["token"]
#                     response = JsonResponse({"token":token,"apikey":user.api_key,"secretkey":user.secret_key},status=200)
#                     response['Access-Control-Allow-Origin'] ='*'
#                     return response
#                 response = HttpResponse("Wrong Password",status=401)
#                 response['Access-Control-Allow-Origin'] ='*'                
#                 return response
#             response = HttpResponse("Invalid name",status = 400)
#             response['Access-Control-Allow-Origin'] ='*'                
#             return response
#         except KeyError:
#             response = JsonResponse({'message': "INVALID_KEYS"}, status =400)
#             response['Access-Control-Allow-Origin'] ='*'  
#             return response
