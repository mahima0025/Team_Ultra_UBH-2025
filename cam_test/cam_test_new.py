# grab_frame.py
import cv2, time, sys
DEV = '/dev/video0'
cap = cv2.VideoCapture(DEV, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Prefer MJPG first (USB cams), else fall back to YUYV
for fourcc, size in [( 'MJPG', (1280,720) ), ( 'UYVY', (640,480) )]:
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    time.sleep(0.2)
    ok, frm = cap.read()
    if ok and frm is not None:
        print(f"Using {fourcc} {size}, shape={frm.shape}")
        break
else:
    sys.exit("Failed to grab frame—check v4l2 formats or device busy.")

cv2.imwrite("frame.jpg", frm)
cap.release()
print("Wrote frame.jpg")

