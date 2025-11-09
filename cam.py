import cv2, sys
devs=[0,1,2,3]
cap=None
for d in devs:
    c=cv2.VideoCapture(d)
    ok,_=c.read()
    if ok: cap=c; print("Using /dev/video%d" % d); break
    c.release()
if cap is None: sys.exit("No camera found")
# prefer MJPG for higher FPS over USB
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
ok,frame=cap.read()
print("capture_ok:", ok, "| shape:", getattr(frame,"shape",None))
if ok: cv2.imwrite("frame.jpg", frame)
cap.release()
