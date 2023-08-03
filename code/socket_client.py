#-*-coding:utf-8-*- 
from pose_detect import *
import threading
import cv2
import os
import time
import socket
import logging
import traceback

logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='a+',
  format='[%(asctime)s %(levelname)-8s %(levelno)s] %(message)s',
  datefmt='%Y%m%d %H:%M:%S',
  encoding='utf-8'
  )

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
  logging.info('Testing Connect...')
  while True:
    try:
        is_connect = False
        s.settimeout(1)
        s.connect((HOST, PORT))
        is_connect = True
        print("Testing Connect Success")
        logging.info('Testing Connect Success')
        break
    except socket.timeout as e:
      print("Testing Connect Timeout:", e)
      logging.warning("Testing Connect Timeout: " + str(e))
      time.sleep(2)
    except Exception as e:
      print(e)
      logging.error("Testing Connect Failed: " + str(e))
      if str(e) == "[WinError 10056] 對一個已連線的通訊端發出連線要求。":
        is_connect = True
      break

def detect_frame():
    # For webcam input:
    try:
      while True:
        pose = "noPose"
        lock.acquire()
        image = global_frame.copy()
        lock.release()

        pose, hand_landmark = hands_detect(image)
        print(pose)
        if hand_landmark:
          image = draw_hand_landmarks(image, hand_landmark)
        try:
          if is_connect :
            s.sendall(bytes(pose, encoding='utf-8'), )
            data = s.recv(1024)
            # print('Received', repr(data))
        except Exception as e:
          error_str = traceback.format_exc()
          print(error_str)
          logging.error("send message Failed: " + str(error_str))
          if str(e) == "[WinError 10054] 遠端主機已強制關閉一個現存的連線。":
            os._exit(0)


        image = cv2.flip(image, 1)
        # cv2.putText(image, pose, (10,40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('MediaPipe hands', image)
       
        if cv2.waitKey(1) == ord('q'):
            break    # 按下 q 鍵停止
    except Exception as e:
      error_str = traceback.format_exc()
      print(error_str)
      logging.error("detect_frame Failed: " + str(error_str))
    finally:
      s.close()


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