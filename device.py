from jtop import jtop
class Jetson:
    def __init__(self):
        self.jetson = jtop()
        self.jetson.start()
        self.mode = self.isJetson()

    #functions
    getArchitecture = lambda self: self.getPlatform()['Machine'] 
    isJetson = lambda self: True if self.getArchitecture() == 'aarch64' else False
    getPlatform = lambda self: self.jetson.board['platform']
    getStats = lambda self: self.jetson.json(self.jetson.stats) 
    getHardware = lambda self: self.getPlatform()['Machine'] 

    def getStatus(self) -> dict:
        if self.mode:
            stats = self.jetson.stats
            data = {
                'CPU': round(self.jetson.cpu['total']['user'], 2),
                'Fan pwmfan0': round(stats['Fan pwmfan0'], 2),
                'RAM': round(stats['RAM'], 2),
                'SWAP': round(stats['SWAP'], 2),
                'GPU': round(stats['GPU'], 2),
                'Temp CPU': round(stats['Temp cpu'], 2),
                'Temp GPU': round(stats['Temp gpu'], 2),
                'time': stats['time'],
                'uptime': stats['uptime'],
                'nvp model': stats['nvp model'],
                'jetson_clocks': stats['jetson_clocks']}
            return data
        else:
            return False
    
    def stop(self):
        self.jetson.close()
    def __del__(self):
        self.stop()

if __name__ == "__main__":
    jet = Jetson()
    data = jet.getStatus()
    print(data)