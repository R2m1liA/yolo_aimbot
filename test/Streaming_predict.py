import cv2
from ultralytics import YOLO

# Load the model
model = YOLO('../apex_v5.pt')

# Load the video
video_path = 'test.mkv'
cap = cv2.VideoCapture(video_path)

# Loop Through the video
while cap.isOpened():
    success, frame = cap.read()
    
    if success:
        # Predict the frame
        results = model(frame)

        annotated_frame = results[0].plot()

        cv2.imshow('frame', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()