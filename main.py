
from yamlParser import YamlHandler
from cam import Cam
from counter import ObjectCounter
from threadManager import MonitoredThread
from queue import Queue
from device import Jetson
from LedProcess import sendDataToWrite
from screen import Ekran
from commonModules.dbmanage import DatabaseManager
from argParser import parseArguments

import time


def main():
    """
    Main function to initialize and manage threads for object detection and status updates.

    Parameters:
    None

    Returns:
    None
    """

    parsedArgs = parseArguments() # Komut satırından gelen FPS gibi değerleri alır.
                                    # argParser.py modülünde detaylıca açıklanmıştır.

    led = Ekran('/dev/ttyUSB1') # USB1 portundan ekranı başlatır.

    db_manager = DatabaseManager() # Veritabanı yöneticisini başlatır.
    device = Jetson() # Jetson cihazını başlatır.
    counter = ObjectCounter(db_manager, 0) # Nesne sayacı başlatılır.
    personCamIp, bicycleCamIp0 = counter.cfg.getIpSource() # Yaya ve Bisikleret kameralarının IP adreslerini alır.



    namesOfThreads = YamlHandler("configs/threadNames.yaml") # Yaml dosyasından thread isimlerini alır.
    threadNames = namesOfThreads.data['threadNames'] # threadNames değişkenine atar.
    queue = Queue(maxsize=200)



    personCam = Cam(personCamIp, 0) # Yaya kamerasını başlatır.

    bicycleCam0= Cam(bicycleCamIp0, 1) # Bisiklet kamerasını başlatır. 



    # Yaya kamerasından gelen görüntüleri işlemek için thread oluşturur.
    capture_thread1 = MonitoredThread(
        target=personCam.putToFrameQueue, 
        args=(queue, parsedArgs.personCamFps), 
        thread_name=threadNames[0],
        critical=True
        )


     # Bisiklet kamerasından gelen görüntüleri işlemek için thread oluşturur.
    capture_thread2 = MonitoredThread(
        target=bicycleCam0.putToFrameQueue, 
        args=(queue, parsedArgs.bicycleCamFps), 
        thread_name=threadNames[1],
        critical=True
        )
    
    # Nesne sayacı tarafından işlenecek görüntüleri işlemek için thread oluşturur.
    processThread = MonitoredThread(
        target=counter.process_frames, 
        args=(queue,), 
        thread_name=threadNames[2],
        critical=True 
        )

    led_thread= MonitoredThread(
        target=sendDataToWrite, 
        args=(led, db_manager, 10), 
        thread_name=threadNames[3], 
        critical=False
        )

    led_thread.start()
    capture_thread1.start()
    capture_thread2.start()
    processThread.start()

    # Sistemin durumunu sürekli olarak güncelleyen bir döngü başlatır ve DB'ye yazar.
    while True:
        mainStatuses = {
        'CaptureThread1': capture_thread1.status,
        'CaptureThread2': capture_thread2.status,
        'ProcessThread': processThread.status,
        'QueueStatus': queue.qsize(),
        'led_thread': led_thread.status,
        }
        deviceStatuses = device.getStatus()
        counter.db.updateMainStatuses(mainStatuses)
        counter.db.updateDeviceStatus(deviceStatuses)
        time.sleep(10)


if __name__ == "__main__":
    main()
