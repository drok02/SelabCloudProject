"one_init": {
    "type": "OS::Heat::CloudConfig",
    "properties": {
        "cloud_config": {
            "bootcmd": 
            [
                "mkdir /home/ubuntu/bong"
            ]
        }
    }
},
,
                                "user_data":{"get_resource": "one_init"}