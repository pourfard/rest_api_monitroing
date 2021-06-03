import json
import time

import requests

CONFIG_PATH = "config.json"

with open(CONFIG_PATH) as f:
    config = json.loads(f.read())


class ServiceMonitor:
    def __init__(self, service_prop):
        self.prop = service_prop
        self.is_updated = False

    def main(self):
        while True:
            try:
                self.check()
            except Exception as e:
                # write the exception in the file
                pass
            time.sleep(self.prop["period"])

    def check(self):
        data = {}
        files = {}
        json_data = {}
        auth = None
        if "auth" in self.prop:
            if self.prop["auth"]["type"] == "basic":
                auth = (self.prop["auth"]["username"], self.prop["auth"]["password"])

        if "payload" in self.prop:
            if "form_data" in self.prop["payload"]:
                for form_data in self.prop["payload"]["form_data"]:
                    if form_data["type"] == "text":
                        data[form_data["key"]] = form_data["value"]
                    elif form_data["type"] == "file":
                        files[form_data["key"]] = open(form_data["value"], 'rb')
            if "json" in self.prop["payload"]:
                json_data = self.prop["payload"]["json"]

        response = None
        if self.prop["method"] == "POST":
            response = requests.post(self.prop["url"], data=data, json=json_data, files=files, auth=auth)
        elif self.prop["method"] == "GET":
            response = requests.get(self.prop["url"], data=data, json=json_data, files=files, auth=auth)

        if response and response.status_code == 200:
            if "response" in self.prop:
                if self.prop["response"]["type"] == "file":
                    pass  # write response.content in the file
                elif self.prop["response"]["type"] == "json":
                    pass  # write response.json in the file
                else:
                    pass  # write response.status_code in the file
        else:
            pass  # write response.status_code in the file


inherited_properties = ["period", "auth", "method", "response"]

for group in config:
    for service in group:
        for key in inherited_properties:
            if key not in service and key in group:
                service[key] = group[key]
