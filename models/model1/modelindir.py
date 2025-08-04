from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.export(format="engine") 
model = YOLO("yolov8s.pt")
model.export(format="engine") 
model = YOLO("yolov8m.pt")
model.export(format="engine") 
model = YOLO("yolov8l.pt")
model.export(format="engine") 
model = YOLO("yolov8x.pt")
model.export(format="engine") 
