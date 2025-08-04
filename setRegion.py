import argparse
import cv2
import numpy as np

from cam import Cam
from yamlParser import YamlHandler
import cv2
import numpy as np

points = []

def draw_polygon(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN: 
        points.append([x, y])
    elif event == cv2.EVENT_RBUTTONDOWN:  
        if points:
            points.pop()

def changeRegion(cam):
    global points
    while True:
        frame = cam.testGetFrame()
        
        # Seçilen noktaları göster
        for point in points:
            cv2.circle(frame, tuple(point), 5, (0, 0, 255), -1)
        
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('j'):  # 'j' tuşuna basıldığında poligon çiz
            if len(points) > 2:  # En az 3 nokta olmalı
                cv2.polylines(frame, [np.array(points)], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.imshow("Frame", frame)
                cv2.waitKey(1)  # Çizilmiş poligon ile pencereyi güncelle

        elif key == ord('q'):  # 'q' tuşuna basıldığında döngüden çık
            break

    return points




if __name__ == "__main__":
    
    points = []

    # parser = argparse.ArgumentParser(description='Video processing and data sending script.')
    # parser.add_argument('--back', type=bool, default=0, help='Path to the first video file.')
    # args = parser.parse_args()
    
    cfg = YamlHandler("configs/config.yaml")

    frontCamAdress, backCamAdress = cfg.getIpSource()
    
    videoPath = "video/bes.mp4"

    cam1 = Cam(backCamAdress, 0)

    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", draw_polygon)


    cfg.update(changeRegion(cam1), 'counterPerson', 'regionPoints')

    # if args.back:
    #     cam = Cam(backCamAdress)
    #     cfg.update(changeRegion(cam1), 'regionPoints', 'RP1')
    # else:
    #     cam = Cam(frontCamAdress)
    #     cfg.update(changeRegion(cam1), 'regionPoints', 'RP2')
    

    cfg.save()

    cv2.destroyAllWindows()



