from ultralytics import YOLO, solutions
from yamlParser import YamlHandler
from datetime import datetime
from commonModules.dbManage import DatabaseManager


class ObjectCounter:
    def __init__(self, _db, viewFlag=False):
        self.cfg = YamlHandler("configs/config.yaml")
        self.identity = YamlHandler('configs/identity.yaml')
        self.personClass = {0: 'person'} 
        self.bicycleClass = {1: 'bicycle'}
        self.totalPerson = 0
        self.totalBicycle = 0
        self.modelPerson = None
        self.modelBicycle = None
        self.counterPerson = None
        self.counterBicycle = None
        self.viewFlag = viewFlag
        self.loadBicycleModel()
        self.loadPersonModel()
        self.loadCounterBicycle()
        self.loadCounterPerson()
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.db = _db
        self.db.setIdentity(self.identity.data.get('clientId', ''),
                            self.identity.data.get('clientSecret', ''),
                            self.identity.data.get('deviceId', 0) )

    def loadCounterPerson(self):
        self.counterPerson = solutions.ObjectCounter(
            self.personClass,
            view_img=self.viewFlag,
            reg_pts= self.cfg.getDataWithKey('counterPerson','regionPoints'),
            draw_tracks=True,
            line_thickness=2
        )
    
    def loadCounterBicycle(self):
        self.counterBicycle = solutions.ObjectCounter(
            self.bicycleClass,
            view_img=self.viewFlag,
            reg_pts= self.cfg.getDataWithKey('counterBicycle','regionPoints'),
            draw_tracks=True,
            line_thickness=2
        )




    def loadPersonModel(self):
        self.modelPerson = YOLO(model=self.cfg.getDataWithKey('model', 'modelPath1'), task='detect')

    def loadBicycleModel(self):
        self.modelBicycle = YOLO(model=self.cfg.getDataWithKey('model', 'modelPath2') , task='detect')  


    def getPerson(self):
        return (self.counterPerson.class_wise_count.get('person', {}).get('OUT', 0) + 
                self.counterPerson.class_wise_count.get('person', {}).get('IN', 0))
    
    def getBicycle(self):
        return (self.counterBicycle.class_wise_count.get('bicycle', {}).get('OUT', 0) + 
                 self.counterBicycle.class_wise_count.get('bicycle', {}).get('IN', 0))


    def checkPerson(self):
        person = self.getPerson() - self.totalPerson
        if person:
            self.totalPerson += person
        return person
 

    def checkBicycle(self):
        bicycle = self.getBicycle() - self.totalBicycle
        if bicycle:
            self.totalBicycle += bicycle
        return bicycle




    def process_frames(self, frame_queue):
        modelPersonParams = self.cfg.data['modelPerson']
        modelBicycleParams = self.cfg.data['modelBicycle']
        while True:
            if not frame_queue.empty():
                frameobj = frame_queue.get()
                if frameobj.frameID == 0: 
                    tracks = list(self.modelPerson.track(frameobj.frame, 
                                                        persist=True, 
                                                        stream=True,
                                                        tracker="configs/botsort.yaml", 
                                                        classes=modelPersonParams['classesIndex'],
                                                        conf=modelPersonParams['conf'],  
                                                        show=modelPersonParams['show'], 
                                                        verbose=modelPersonParams['verbose'],
                                                        ))
                    self.counterPerson.start_counting(frameobj.frame, tracks)
                    newPerson = self.checkPerson()
                    if newPerson:
                        print("\nPerson: " + str(self.totalPerson))
                        self.db.addJsonData(newPerson, True)

                else: 
                    tracks = list(self.modelBicycle.track(frameobj.frame, 
                                                        persist=True, 
                                                        stream=True,
                                                        tracker="configs/botsort.yaml", 
                                                        classes=modelBicycleParams['classesIndex'],
                                                        conf=modelBicycleParams['conf'],  
                                                        show=modelBicycleParams['show'], 
                                                        verbose=modelBicycleParams['verbose'],
                                                        ))
                    self.counterBicycle.start_counting(frameobj.frame, tracks)
                    newBicycle = self.checkBicycle()
                    if newBicycle:
                        print("\nBicycle: " + str(self.totalBicycle))
                        self.db.addJsonData(newBicycle, False)




