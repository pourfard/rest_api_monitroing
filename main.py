import json
import os.path
from types import SimpleNamespace
from datetime import date, datetime


import time

import requests

CONFIG_PATH = "config.json"

with open(CONFIG_PATH) as f:
    config = json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))

LOG_DIRECTORY = "Logs"


class ServiceMonitor:
    def __init__(self, service_prop):
        self.prop = service_prop
        self.is_updated = False

        self.check()

    def main(self):
        while True:
            try:
                self.check()
            except Exception as e:
                # write the exception in the file
                pass
            time.sleep(self.prop.period)

    def check(self):
        data = {}
        files = {}
        json_data = {}
        auth = None
        if hasattr(self.prop, "auth"):
            if self.prop.auth.type == "basic":
                auth = (self.prop.auth.username, self.prop.auth.password)

        if hasattr(self.prop, "payload"):
            if hasattr(self.prop.payload, "form_data"):
                for form_data in self.prop.payload.form_data:
                    if form_data.type == "text":
                        data[form_data.key] = form_data.value
                    elif form_data.type == "file":
                        files[form_data.key] = open(form_data.value, 'rb')
            if hasattr(self.prop, "json"):
                json_data = self.prop.payload.json

        response = None
        if self.prop.method == "POST":
            response = requests.post(self.prop.url, data=data, json=json_data, files=files, auth=auth)
        elif self.prop.method == "GET":
            response = requests.get(self.prop.url, data=data, json=json_data, files=files, auth=auth)

        save_directory = os.path.join(LOG_DIRECTORY, service.group_name, service.name)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"),service.group_name + " -> " + service.name + " -> " + str(response.status_code))
        if response and response.status_code == 200:
            if hasattr(self.prop, "response"):
                if self.prop.response.type == "file":
                    pass  # write response.content in the file
                elif self.prop.response.type == "json":
                    file_name = os.path.join(save_directory,str(time.time())+"_200.json")

                    with open(file_name, "w+") as f:
                        f.write(json.dumps(response.json()))
                else:
                    pass  # write response.status_code in the file
        else:
            file_name = os.path.join(save_directory, str(time.time()) +"_"+str(response.status_code)+ ".txt")

            with open(file_name, "w+") as f:
                f.write(response.text)


inherited_properties = ["period", "auth", "method", "response", "group_name"]

for group in config.groups:
    for service in group.services:
        for key in inherited_properties:
            if not hasattr(service, key) and hasattr(group, key):
                setattr(service, key, getattr(group, key))
        ServiceMonitor(service)
