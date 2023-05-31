import cv2
from ultralytics import YOLO

img = cv2.imread('1.jpg')
model = YOLO('apex_v8.pt')
results = model(img)
res_plot = results[0].plot()
cv2.imshow('res_plot', res_plot)
cv2.waitKey(0)