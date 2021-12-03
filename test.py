from django.shortcuts import render
import json
import requests
from django.views import View
from django.http import HttpResponse, JsonResponse

# 토큰 받아오기
class AccountView():
    def post():
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
        auth_res = requests.post("http://164.125.70.22/identity/v3/auth/tokens",
            headers = {'content-type' : 'application/json'},
            data = json.dumps(token_payload))

        #발급받은 token 출력
        admin_token = auth_res.headers["X-Subject-Token"]
        # print("token",admin_token)
        return admin_token

    def create_user():
        #openstack 사용자 생성
        admin_token= AccountView.post()
        # 사용자의 openstack 정보 
        
        openstack_uesr_payload = {
            "user": {
                "name": 'python_test',
                "password": '0000',
                "default_project_id": "306a781cdcfe4bb7ae7ff1f8bbba6596"
            }
        }
        user_res = requests.post("http://164.125.70.22/identity/v3/users",
            headers = {'X-Auth-Token' : admin_token},
            data = json.dumps(openstack_uesr_payload))
        print(user_res.json())
        # print("사용자 이름은 :",openstack_uesr_payload["user"]["name"])
        return openstack_uesr_payload["user"]["name"]


    def delete_user():
        admin_token= AccountView.post()
        user_res= requests.get("http://164.125.70.22/identity/v3/users?name=python_test",
            headers = {'X-Auth-Token' : admin_token})
        user_id=user_res.json()
        user_detail=user_id["users"][0]["id"]    
        
        print(user_detail) 
        
        user_res = requests.delete("http://164.125.70.22/identity/v3/users/{id}".format(id=user_detail),
            headers = {'X-Auth-Token' : admin_token}
            )
        print("사용자 삭제 완료")
        # openstack_id = user_res.json()["user"]["id"]
        # group_res = requests.put("http://164.125.70.22/identity/v3/groups/65d8b8f223c249dbb5c316b3c604bea2/users/"+ openstack_id,
        #     headers = {'X-Auth-Token' : admin_token})

        # permission_req = requests.put("http://164.125.70.22/identity/v3/domains/default/users/"+openstack_id+"/roles/a72b87b6428c4a568b4116b2a500da9b")
        # response = JsonResponse(data2,status = 200)
        # response['Access-Control-Allow-Origin'] ='*'
        # return response
    def signin():
        admin_token= AccountView.post()
        

def main():
    # d= AccountView.post()
    # c=AccountView.create_user()
    f= AccountView.delete_user()
        
main()
#         #openstack 사용자 생성
#         user_res = requests.post("http://164.125.70.22/identity/v3/users",
#             headers = {'X-Auth-Token' : admin_token},
#             data = json.dumps(openstack_uesr_payload))
#         print(user_res.json())

#         #openstack id 확인
#         # 생성된 사용자를 admins 그룹에 추가

#         openstack_id = user_res.json()["user"]["id"]
#         group_res = requests.put("http://164.125.70.22/identity/v3/groups/65d8b8f223c249dbb5c316b3c604bea2/users/"+ openstack_id,
#             headers = {'X-Auth-Token' : admin_token})

#         permission_req = requests.put("http://164.125.70.22/identity/v3/domains/default/users/"+openstack_id+"/roles/a72b87b6428c4a568b4116b2a500da9b")
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
#     def post(self, request):
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
#                     auth_res2 = requests.post("http://52.78.82.160:7014/token",
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
