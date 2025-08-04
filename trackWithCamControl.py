from yamlParser import YamlHandler
from cam import Cam
from counter import ObjectCounter
from threadManager import MonitoredThread
from queue import Queue
import cv2
import argparse
import time
from commonModules.dbManage import DatabaseManager

def parseArguments():
    parser = argparse.ArgumentParser(description='Video processing and data sending script.')
    parser.add_argument('--personCam', type=int, default=1, help='source for cam1; 1 for iptv on personcam ; 0 for videopath on personcam')
    parser.add_argument('--bicycleCam', type=int, default=1, help='source for cam2; 1 for iptv on bicyclecam ; 0 for videopath on bicyclecam')
    parser.add_argument('--reverse', type=int, default=0, help='1 for bicycleCounter on Personcam else 0')
    parser.add_argument('--personCamFps', type=int, default=0, help='Cam fps for personcam')
    parser.add_argument('--bicycleCamFps', type=int, default=0, help='Cam fps for backCam')

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    parsedArgs = parseArguments()

    cfg = YamlHandler("configs/config.yaml")
    personCamIp, bicycleCamIp = cfg.getIpSource()
    namesOfThreads = YamlHandler("configs/threadNames.yaml")
    threadNames = namesOfThreads.data['threadNames']
    
    video_source1 = personCamIp
    video_source2 = bicycleCamIp

    if parsedArgs.personCam:
        personCam = Cam(personCamIp, parsedArgs.reverse)
    else:
        personCam = Cam(video_source1, parsedArgs.reverse)
        
    if parsedArgs.bicycleCam:
        bicycleCam = Cam(bicycleCamIp, not parsedArgs.reverse)  
    else:
        bicycleCam = Cam(video_source2, not parsedArgs.reverse)
     
    db_manager = DatabaseManager()
    Counter = ObjectCounter(db_manager)
  
    queue = Queue(maxsize=100) 

    capture_thread1 = MonitoredThread(
        target=personCam.putToFrameQueue, 
        args=(queue, parsedArgs.personCamFps), 
        thread_name=threadNames[0],
                                      )
    
    capture_thread2 = MonitoredThread(
        target=bicycleCam.putToFrameQueue, 
        args=(queue, parsedArgs.bicycleCamFps), 
        thread_name=threadNames[1],
                                      )

    processThread = MonitoredThread(
        target=Counter.process_frames, 
        args=(queue,), 
        thread_name=threadNames[2], 
        )


    capture_thread1.start()
    capture_thread2.start()
    processThread.start()


    while Counter.counterPerson.im0 is None or Counter.counterBicycle.im0 is None:
        print("Bekleniyor...")  # Kontrol amaçlı terminale yazdırma
        time.sleep(0.5)  # 1 saniye bekle, CPU'yu yormamak için küçük bir bekleme süresi ekleniyor

    # Koşul sağlandıktan sonra pencere oluştur ve while döngüsüne gir
    cv2.namedWindow('frontCam')
    cv2.namedWindow('backCam')

    try:
        while True:
            cv2.imshow('frontCam', Counter.counterPerson.im0)
            cv2.imshow('backCam', Counter.counterBicycle.im0)
            
            # 'q' tuşuna basılırsa döngüyü kır
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Program sonlandırılıyor...")
                break
    finally:
        # Pencereleri kapat
        cv2.destroyAllWindows()

        # Thread'leri durdur
        capture_thread1.stop()
        capture_thread2.stop()
        processThread.stop()

        # Thread'lerin sonlanmasını bekle
        capture_thread1.join()
        capture_thread2.join()
        processThread.join()

        print("Tüm thread'ler durduruldu, program sonlandırıldı.")
