# grab_frame.py
import cv2, time, sys
DEV = '/dev/video0'

cap = cv2.VideoCapture(DEV, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                     
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
time.sleep(0.2)
ok, frm = cap.read()
if ok and frm is None:
    print('Error')

cv2.imwrite("frame2.jpg", frm)
cap.release()
print("Wrote frame2.jpg")
