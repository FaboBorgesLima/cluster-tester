from server_system_monitor import Monitor
import json

config = open(__file__.replace("__main__.py","") + "/../db/config_example.json",'r')
config_data = json.load(config)

print(config_data.get("app"))
