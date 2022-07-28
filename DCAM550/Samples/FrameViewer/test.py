import cv2
import numpy as np

f = open("output", "rb")

while True:
    rd = f.read(76800*8)
    frame = np.frombuffer(rd, dtype=np.uint16)
    frame.shape = (480, 640)
    
    img = np.int32(frame)
    img = img * 255 / 5000
    img = np.clip(img, 0, 255)
    img = np.uint8(img)
    cv2.imshow("view", img)
    cv2.waitKey(100)
