from pose_detect import *
import mediapipe as mp
import threading
import cv2
import os
import time
import socket

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

global_frame = ""
lock = threading.Lock()
pose_dict = ["noPose", "SunRight", "SunLeft", "CloseLight", "WindRight", "WindLeft", "Pray", "WindForward"]

HOST = '127.0.0.1'
PORT = 11000

def get_frame():
  global global_frame
  cap = cv2.VideoCapture(0)
  while cap.isOpened():
    success, frame = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue
    lock.acquire()
    global_frame = frame.copy()
    lock.release()
    cv2.imshow("camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()

def detect_frame():
  global global_frame
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # For webcam input:
    with mp_holistic.Holistic(
      static_image_mode=False,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as holistic:
      while True:
        lock.acquire()
        image = global_frame.copy()
        lock.release()

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)

        # Draw landmark annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        pose_idx = classify_pose(results, image)

        if pose_idx is None:
            pose_idx = 0

        s.sendall(bytes(pose_dict[pose_idx], encoding='utf-8'))

        image = draw_landmarks(image, results, mp_holistic, mp_drawing, mp_drawing_styles)
        image = cv2.flip(image, 1)
        if pose_idx != None:
          cv2.putText(image, pose_dict[pose_idx], (10,40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
          cv2.putText(image, pose_dict[0], (10,40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('MediaPipe Holistic', image)

        data = s.recv(1024)
        print('Received', repr(data))
       
        if cv2.waitKey(1) == ord('q'):
            break    # 按下 q 鍵停止



a = threading.Thread(target=get_frame)
a.daemon=True
a.start()
time.sleep(2)
detect_frame()


# while True:
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         s.sendall(bytes(l[0], encoding='utf-8'))
#         data = s.recv(1024)

#     print('Received', repr(data))
#     time.sleep(0.5)