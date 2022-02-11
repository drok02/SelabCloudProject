from django.shortcuts import render
import json
import yaml
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse
import sys

address = "192.168.0.48"
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
    
    # stack 생성. 
    def create_stack():
        admin_token= AccountView.token()
        stack_name= input("stack 이름 입력 : ")
        key_name= input("key 이름 입력 : ")
        server_name= input("server 이름 입력 : ")
        openstack_stack_payload ={
                                
                "stack_name": "bong",
                "template": {
                    "heat_template_version": "2021-04-16T00:00:00.000Z",
                    "description": "This template demonstrates the different ways configuration resources can be used to specify boot-time cloud-init configuration.",
                    "resources": {
                    "mybox": {
                        "type": "OS::Nova::Server",
                        "properties": {
                        "name": "mybox_summitExtension",
                        "flavor": "ds512M",
                        "image": "ubuntu",
                        "key_name": {
                            "get_resource": "demo_key"
                        },
                        "networks": [
                            {
                            "port": {
                                "get_resource": "mybox_management_port"
                            }
                            }
                        ],
                        "user_data": {
                            "get_resource": "myconfig"
                        },
                        "user_data_format": "RAW"
                        }
                    },
                    "myconfig": {
                        "type": "OS::Heat::CloudConfig",
                        "properties": {
                        "cloud_config": {
                            "package_update": "true",
                            "package_upgrade": "true",
                            "users": [
                            "default",
                            {
                                "name": "bong",
                                "shell": "/bin/bash",
                                "sudo": "ALL=(ALL) NOPASSWD:ALL"
                            }
                            ],
                            "ssh_pwauth": "true",
                            "write_files": [
                            {
                                "path": "/tmp/one",
                                "content": "The one is bar"
                            }
                            ],
                            "bootcmd": [
                            "mkdir /home/ubuntu/bong"
                            ],
                            "chpasswd": {
                            "list": "root:1111\n",
                            "expired": "false"
                            },
                            "manage_home_ubuntu": "false",
                            "packages": [
                            "apache2",
                            "net-tools",
                            "pwgen",
                            "pastebinit"
                            ]
                        }
                        }
                    },
                    "demo_key": {
                        "type": "OS::Nova::KeyPair",
                        "properties": {
                        "name": "test-key4"
                        }
                    },
                    "mybox_management_port": {
                        "type": "OS::Neutron::Port",
                        "properties": {
                        "network_id": {
                            "get_resource": "mynet"
                        },
                        "security_groups": [
                            {
                            "get_resource": "mysecurity_group"
                            }
                        ]
                        }
                    },
                    "server_floating_ip": {
                        "type": "OS::Neutron::FloatingIP",
                        "properties": {
                        "floating_network_id": "bebea9a2-08a6-4b4a-a4e3-a9aaeefa6b22",
                        "port_id": {
                            "get_resource": "mybox_management_port"
                        }
                        }
                    },
                    "mynet": {
                        "type": "OS::Neutron::Net",
                        "properties": {
                        "name": "management-net"
                        }
                    },
                    "mysub_net": {
                        "type": "OS::Neutron::Subnet",
                        "properties": {
                        "name": "management-sub-net",
                        "network_id": {
                            "get_resource": "mynet"
                        },
                        "cidr": "10.0.0.0/24",
                        "gateway_ip": "10.0.0.1",
                        "enable_dhcp": "true",
                        "dns_nameservers": [
                            "8.8.8.8",
                            "8.8.4.4"
                        ]
                        }
                    },
                    "mysecurity_group": {
                        "type": "OS::Neutron::SecurityGroup",
                        "properties": {
                        "name": "mysecurity_group",
                        "rules": [
                            {
                            "remote_ip_prefix": "0.0.0.0/0",
                            "protocol": "tcp",
                            "port_range_min": 22,
                            "port_range_max": 22
                            },
                            {
                            "remote_ip_prefix": "0.0.0.0/0",
                            "protocol": "icmp",
                            "direction": "ingress"
                            }
                        ]
                        }
                    },
                    "router": {
                        "type": "OS::Neutron::Router"
                    },
                    "router_gateway": {
                        "type": "OS::Neutron::RouterGateway",
                        "properties": {
                        "router_id": {
                            "get_resource": "router"
                        },
                        "network_id": "bebea9a2-08a6-4b4a-a4e3-a9aaeefa6b22"
                        }
                    },
                    "router_interface": {
                        "type": "OS::Neutron::RouterInterface",
                        "properties": {
                        "router_id": {
                            "get_resource": "router"
                        },
                        "subnet_id": {
                            "get_resource": "mysub_net"
                        }
                        }
                    }
                    }
                }
                
            }  
        with open('C:/Users/PC/bong/SelabCloudProject/jsontest.json','r') as f:
            json_data=json.load(f)
        user_res = requests.post("http://"+address+"/heat-api/v1/e90ed7ec3ac84590852a635c81b40d1d/stacks",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_stack_payload))
        print("stack생성 ",user_res)



    def create_stack_yaml():
        with open('/Users/ibonghun/Desktop/test/SelabCloudProject/ex7_private_net_api_ver.yaml') as f:
            yaml_data=yaml.load(f,Loader=yaml.FullLoader)
            admin_token= AccountView.token()
            user_res = requests.post("http://"+address+"/heat-api/v1/70cbbe815ccc46c8bb3dc86a452b4437/stacks",
                headers = {'X-Auth-Token' : admin_token},
                data = yaml.dump(yaml_data))
            print("stack생성 ",user_res)
            # print("yaml데이터는 : ",yaml_data)
          

    def loader():
        with open('G:\내 드라이브\google_학부연구생\SELAB\SelabCloudProject\ex5_api_ver.yaml') as f:
            print("yaml파일 내용: \n")
            yaml_data=yaml.load(f,Loader=yaml.FullLoader)
            print(yaml_data)
            # for item in yaml_data:
                # print(item)
    def jsonprint():
        with open('/Users/ibonghun/Desktop/test/SelabCloudProject/jsontest.json','r') as f:
            json_data=json.load(f)
        # print(json.dumps(json_data))
        return json.dumps(json_data)        
def main():
    # d= AccountView.token()
    # c=AccountView.create_user()
    # f= AccountView.delete_user()
    #f=AccountView.create_instance()
    # f=AccountView.create_img_from_server()
    # f=AccountView.create_snapshot()
    # f=AccountView.create_vol()
    # f=AccountView.create_flavor()
     f=AccountView.create_stack()
    #   f=AccountView.create_stack_yaml()
        # f=AccountView.loader()
    # f=AccountView.jsonprint()
    # print(f)
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
