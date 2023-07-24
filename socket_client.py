from pose_detect import *
import mediapipe as mp
import threading
import cv2
import os
import time
import socket

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

global_frame = ""
lock = threading.Lock()
pose_dict = ["noPose", "SunRight", "SunLeft", "CloseLight", "WindRight", "WindLeft", "Pray", "WindForward"]

HOST = '127.0.0.1'
PORT = 11000

is_connect = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    # cv2.imshow("camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()

def test_connect():
  global is_connect
  print("Testing Connect...")
  while True:
    try:
        s.settimeout(0.01)
        s.connect((HOST, PORT))
        is_connect = True
        print("Testing Connect Success")
        break
    except Exception as e:
      print(e)
      time.sleep(2)

def detect_frame():
    # For webcam input:
    with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
      while True:
        pose = "noPose"
        try:
          lock.acquire()
          image = global_frame.copy()
          width, height = image.shape[1], image.shape[0]
          lock.release()

          # To improve performance, optionally mark the image as not writeable to
          # pass by reference.
          image.flags.writeable = False
          image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
          results = hands.process(image)

          # Draw landmark annotation on the image.
          image.flags.writeable = True
          image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

          if results.multi_hand_landmarks:
                finger_points = []
                hand_landmark = next(iter(results.multi_hand_landmarks))
                mp_drawing.draw_landmarks(image, hand_landmark, mp_hands.HAND_CONNECTIONS)
                for i in hand_landmark.landmark:
                    i.x = i.x * width
                    i.y = i.y * height
                if hand_landmark.landmark:
                    angle_list = cal_hand_angles(hand_landmark.landmark)
                    pose = pose_detect(angle_list)
                    print(pose)
          try:
            if is_connect :
              s.sendall(bytes(pose, encoding='utf-8'), )
              data = s.recv(1024)
              print('Received', repr(data))
          except Exception as e:
            print(e)

          image = cv2.flip(image, 1)
          cv2.putText(image, pose, (10,40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
          cv2.imshow('MediaPipe hands', image)
         
          if cv2.waitKey(1) == ord('q'):
              break    # 按下 q 鍵停止
        except Exception as e:
          print(e)


a = threading.Thread(target=get_frame)
a.daemon=True
a.start()
time.sleep(2)
b = threading.Thread(target=test_connect)
b.daemon = True
b.start()
time.sleep(2)
detect_frame()


# while True:
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         s.sendall(bytes(l[0], encoding='utf-8'))
#         data = s.recv(1024)

#     print('Received', repr(data))
#     time.sleep(0.5)