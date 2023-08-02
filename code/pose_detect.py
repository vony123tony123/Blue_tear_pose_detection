from AngleDef import *
import mediapipe as mp
import math
import cv2
import copy

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 根據兩點的座標，計算角度
def cal_vector2D_angle(v1, v2):
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
    except:
        angle = 180
    return angle

# 根據傳入的 21 個節點座標，得到該手指的角度
def cal_hand_angles(hand):
    angle_list = []
    for _, points in FINGER_ANGLE_POINTS.items():
        angle = angle = cal_vector2D_angle(
        ((int(hand[points[0]].x)- int(hand[points[1]].x)),(int(hand[points[0]].y)-int(hand[points[1]].y))),
        ((int(hand[points[2]].x)- int(hand[points[3]].x)),(int(hand[points[2]].y)- int(hand[points[3]].y)))
        )
        angle_list.append(angle)
    return angle_list

def pose_detect(hand_angles):
    # results = [("彎曲", angle) if angle >= 50 else ("伸直", angle) for angle in hand_angles ]
    results = [False if angle >= 50 else True for angle in hand_angles ]
    if results == [True, True, False, False, False]:
        return "WindForward"
    elif results == [True, False, False, False, False]:
        return "Pray"
    elif results == [False, True, True, False, False]:
        return "SunRight"
    elif results == [False, False, False, False, False]:
        return "CloseLight"
    else:
        return "noPose"

def hands_detect(image):
    width, height = image.shape[1], image.shape[0]
    pose = "noPose"
    hand_landmark_origin = None
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
        hand_landmark_origin = copy.copy(hand_landmark)
        for i in hand_landmark.landmark:
            i.x = i.x * width
            i.y = i.y * height
        if hand_landmark.landmark:
            angle_list = cal_hand_angles(hand_landmark.landmark)
            pose = pose_detect(angle_list)
    return pose, hand_landmark_origin

def draw_hand_landmarks(image, hand_landmark):
    mp_drawing.draw_landmarks(image, hand_landmark, mp_hands.HAND_CONNECTIONS)
    return image

if __name__ == '__main__':
    # For webcam input:
    cap = cv2.VideoCapture(0)
    mp_drawing = mp.drawing_utils
    mp_drawing_styles = mp.drawing_styles
    mp_hands = mp.solutions.hands
    with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            success, image = cap.read()
            width, height = image.shape[1], image.shape[0]
            if not success:
              print("Ignoring empty camera frame.")
              # If loading a video, use 'break' instead of 'continue'.
              continue

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
                    print(pose_detect(angle_list))

            # Flip the image horizontally for a selfie-view display.
            # cv2.imshow('MediaPipe Holistic', cv2.flip(image, 1))
            cv2.imshow('MediaPipe Holistic', image)
            if cv2.waitKey(1) & 0xFF == 27:
              break
    cap.release()




