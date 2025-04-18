# import cv2

# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("❌ Cannot open camera")
#     exit()

# ret, frame = cap.read()
# if not ret:
#     print("❌ Can't receive frame (stream end?). Exiting ...")
# else:
#     cv2.imwrite("test_frame.jpg", frame)
#     print("✅ Frame captured to test_frame.jpg")

# cap.release()

from picamera2 import Picamera2
import time

picam2 = Picamera2()
picam2.start()

for i in range(10):
    frame = picam2.capture_array()
    print(f"✅ Frame {i+1} captured")
    time.sleep(1)


