
from yamlParser import YamlHandler
from cam import Cam
from counter import ObjectCounter
from threadManager import MonitoredThread
from queue import Queue
from device import Jetson
from LedProcess import sendDataToWrite
from screen import Ekran
from commonModules.dbManage import DatabaseManager
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

    parsedArgs = parseArguments()

    led = Ekran('/dev/ttyUSB1')

    db_manager = DatabaseManager()
    device = Jetson()
    counter = ObjectCounter(db_manager, 0)
    personCamIp, bicycleCamIp0 = counter.cfg.getIpSource()



    namesOfThreads = YamlHandler("configs/threadNames.yaml")
    threadNames = namesOfThreads.data['threadNames']

    queue = Queue(maxsize=200)



    personCam = Cam(personCamIp, 0)

    bicycleCam0= Cam(bicycleCamIp0, 1) 




    capture_thread1 = MonitoredThread(
        target=personCam.putToFrameQueue, 
        args=(queue, parsedArgs.personCamFps), 
        thread_name=threadNames[0],
        critical=True
        )

    capture_thread2 = MonitoredThread(
        target=bicycleCam0.putToFrameQueue, 
        args=(queue, parsedArgs.bicycleCamFps), 
        thread_name=threadNames[1],
        critical=True
        )
    

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
