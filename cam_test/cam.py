import cv2, time, sys

OUT_DIR='/dev/video0'
W, H = 1280, 720

cap = cv2.VideoCapture(OUT_DIR, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(3, W)
cap.set(4, H)
time.sleep(0.5)

work, frame = cap.read()
cap.release()

if not work or frame is None:
	sys.exit('No frame from camera')

cv2.imwrite('frame0.jpg', frame)
print('FRAME', frame.shape)
