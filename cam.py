# Sistemin kamera yönetiminden sorumlu modülü.

import cv2  
from errors import RaiseError

import time

class frameObj:
    def __init__(self, frame, frameID:bool): 
        self.frame = frame
        self.frameID = frameID #0 = insan, 1 = bisiklet

# Kamera bağlantısı açmak, kareleri okumak.
class Cam(frameObj):
    def __init__(self, source, bicycleFlag:bool):
        self.source = source # IP kamera adresi.
        self.bicycleFlag = bicycleFlag # 0 = İnsan, 1 = Bisiklet
        self.cap = None
        self.cameraIsOpen = False # Kamera başarıyla açılırsa sistem hazır duruma geçiyor.
        self.openCam()
        self.width, self.height, self.fps = self.getCameraProperties() # Kameranın en boy ve fps özellikleri çekiliyor.


    # Kamera açıksa genişlik, yükseklik, FPS bilgileri döner. 
    def getCameraProperties(self):
        if self.cameraIsOpen:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            return width, height, fps
        else:
           raise RuntimeError("Camera is not open!")

    # Kameradan kayıt açıksa (yani kare yollanıyorsa) okur. Bağlantı koparsa, kare almak için yeniden açmayı dener.
    def getFrame(self):
        if self.cap.isOpened:
            try:
                ret, frame = self.cap.read() 
                if ret:
                        return frame
                else:
                        self.releaseCamera()
                        self.openCam()
                        _ , frame = self.cap.read()
                        if frame is not None:
                            return frame
                        else:
                            raise Exception(RaiseError(0))

            except Exception as e:
                print(f"Hata: {str(e)}")
                
        else:
            self.openCam()

    # Kamera kayıt açılır.
    def openCam(self):
        try:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise Exception(RaiseError(0))  
            else:
                self.cameraIsOpen = True
        except Exception as e:
            print(f"Hata: {str(e)}") 

    # Her halükarda bir kare almamız gerektiği için boş da olsa kare üretir resize etmek için.
    # Sürekli çalışan bir thread yapısı oluşturuyoruz ki gerçek zamanlı kayıtta problem olmasın.
    def testGetFrame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read() ## ret false olsa bile frame'i döndürüyor burası çok önemli dikkat et programı düzenle
            if frame is not None:
                    return cv2.resize(frame, (640, 480))
            else:
                    self.releaseCamera()
                    self.openCam()
                    _ , frame = self.cap.read()
                    return cv2.resize(frame, (640, 480))


    # testGetFrame de elde edilen kareleri kuyruğa koyar. bisiklet ve yaya olarak ayırıp.
    def putToFrameQueue(self, queue, fps):
        while True:
            if fps != 0:
                time.sleep(1/fps)
            Obj = frameObj(self.testGetFrame(), self.bicycleFlag)
            queue.put(Obj)



    def releaseCamera(self):
        if self.cameraIsOpen:
            self.cap.release()
            self.cameraIsOpen = False

    def __del__(self):
        self.releaseCamera()



if __name__ == '__main__':
    from yamlParser import YamlHandler
    cfg = YamlHandler("configs/config.yaml")
    personCamAdress, bicycleCamAdress = cfg.getIpSource() #YamlHandler ---> config dosyasına gider ----> ordan da ipler değişkenlere çekilir.

    camera = Cam(personCamAdress, True)
    cv2.namedWindow("Frame")

    while True:
        frame = camera.getFrame()
        # resized_frame = cv2.resize(frame, (480, 480))
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): 
            break

    cv2.destroyAllWindows()



    
