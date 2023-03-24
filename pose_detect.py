import cv2
import math



def is_hold(landmarks):
  if type(landmarks) == list:
    return False
  fingerTops = [landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
  origin = (landmarks[0].x, landmarks[0].y)
  max_distance = math.dist(origin, (landmarks[10].x, landmarks[10].y))
  result = True
  for fingerTop in fingerTops:
    if math.dist(origin, (fingerTop.x, fingerTop.y)) > max_distance:
      result = False
  return result

def is_open(landmarks):
  if type(landmarks) == list:
    return False
  fingerTops = [landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
  origin = (landmarks[0].x, landmarks[0].y)
  max_distance = math.dist(origin, (landmarks[10].x, landmarks[10].y))
  result = False
  for fingerTop in fingerTops:
    if math.dist(origin, (fingerTop.x, fingerTop.y)) > max_distance:
      result = True
  return result

def draw_landmarks(image, results, mp_holistic, mp_drawing, mp_drawing_styles):
  mp_drawing.draw_landmarks(
    image,
    results.left_hand_landmarks,
    mp_holistic.HAND_CONNECTIONS,
    mp_drawing_styles.get_default_hand_landmarks_style(),
    mp_drawing_styles.get_default_hand_connections_style())

  mp_drawing.draw_landmarks(
    image,
    results.right_hand_landmarks,
    mp_holistic.HAND_CONNECTIONS,
    mp_drawing_styles.get_default_hand_landmarks_style(),
    mp_drawing_styles.get_default_hand_connections_style())

  mp_drawing.draw_landmarks(
    image,
    results.pose_landmarks,
    mp_holistic.POSE_CONNECTIONS,
    landmark_drawing_spec=mp_drawing_styles
    .get_default_pose_landmarks_style())

  return image

def classify_pose(results, image):
  if results.pose_landmarks:
    pose_landmarks = results.pose_landmarks.landmark

    if results.left_hand_landmarks:
      left_hand_landmarks = results.left_hand_landmarks.landmark
    else:
      left_hand_landmarks = []

    if results.right_hand_landmarks:
      right_hand_landmarks = results.right_hand_landmarks.landmark
    else:
      right_hand_landmarks = []

    # ears_dist = math.dist((pose_landmarks[8].x, pose_landmarks[8].y), (pose_landmarks[7].x, pose_landmarks[7].y))
    # wrists_dist = math.dist((pose_landmarks[16].x, pose_landmarks[16].y), (pose_landmarks[15].x, pose_landmarks[15].y))
    ears_dist = abs(pose_landmarks[8].x - pose_landmarks[7].x)
    wrists_dist = abs(pose_landmarks[16].x - pose_landmarks[15].x)
    if results.left_hand_landmarks and results.right_hand_landmarks:
      if  wrists_dist < ears_dist:
        return 6

    left_shoulder = pose_landmarks[11]
    right_shoulder = pose_landmarks[12]

    if is_hold(left_hand_landmarks):
      left_hand_point = left_hand_landmarks[0]
      if left_hand_point.x > left_shoulder.x:
        return 2
      elif left_hand_point.x <= left_shoulder.x and left_hand_point.x >= right_shoulder.x:
        return 3
    if is_hold(right_hand_landmarks):
      right_hand_point = right_hand_landmarks[0]
      if right_hand_point.x < right_shoulder.x:
        return 1
      elif right_hand_point.x <= left_shoulder.x and right_hand_point.x >= right_shoulder.x:
        return 3

    if is_open(left_hand_landmarks) and is_open(right_hand_landmarks):
      nose_point = pose_landmarks[0]
      left_hand_point = left_hand_landmarks[17]
      right_hand_point = right_hand_landmarks[17]
      if left_hand_point.y <= left_shoulder.y and right_hand_point.y <= right_shoulder.y:
        if nose_point.x > left_hand_point.x:
          return 5
        elif nose_point.x < right_hand_point.x:
          return 4
        elif nose_point.x <= left_hand_point.x and nose_point.x >= right_hand_point.x:
          return 7

    return 0







