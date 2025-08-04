import yaml

class YamlHandler:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.data = None
        self.load()

    def load(self):
        with open(self.yaml_path, "r") as file:
            self.data = yaml.safe_load(file)

    def save(self):
        with open(self.yaml_path, "w") as file:
            yaml.safe_dump(self.data, file)

    def update(self, value, *keys):
        d = self.data
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
        self.save()

    def getData(self):
        return self.data
    
    def getDataWithKey(self, *keys):
        d = self.data
        for key in keys:
            d = d.get(key, None)
            if d is None:
                return None
        return d
    
    def setData(self, data):
        self.data = data
        self.save()

    def deleteData(self, *keys):
        d = self.data
        for key in keys[:-1]:
            if key in d:
                d = d[key]
            else:
                raise ValueError("Data does not exist!")
        if keys[-1] in d:
            del d[keys[-1]]
            self.save()
        else:
            raise ValueError("Data does not exist!")

    def getIpSource(self):
        user = self.data['username']
        password = self.data['password']
        _personCamIp = self.data['ip']['personCamIp']
        _bicycleCamIp = self.data['ip']['bicycleCamIp']

        personCamIp = "rtsp://" + user + ":" + password + "@" + _personCamIp 
        bicycleCamIp = "rtsp://" + user + ":" + password + "@" + _bicycleCamIp
        return personCamIp, bicycleCamIp