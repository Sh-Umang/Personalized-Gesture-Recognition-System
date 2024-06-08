import cv2 as cv
import mediapipe as mp
import numpy as np
import pyautogui as pg


import copy
import joblib
import itertools
import csv

from keypoint_classifier_labels import keypoint_classifier_labels
from keybinding import keybinding
from handtracking import HandDetector as hd
from knn_classifier import kNNClassifier
from db_sqlite3 import db_connector

class process:
    def __init__(self):
        self.something = 0
        self.type = 0
        self.left_fingers = []
        self.right_fingers = []
        self.keypoints_count = 0
        self.font = cv.FONT_HERSHEY_SIMPLEX
        self.activation_textCv = "Gesture Recognition Deactive"
        self.gesture_label = "None"
        self.keybind_text = "None"

    @staticmethod
    def process(queue, new_points_csv_path, gesture_id, model_name, _mode, cam_show, profile_id):
        self = process()
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
        self.queue = queue
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode = False,
            max_num_hands = 2,
            min_detection_confidence = 0.7,
            min_tracking_confidence = 0.5,
        )

        mode = _mode
        count = 0
        iterate = True
        temp_hand_sign_id = -1

        

        while True:

            key = cv.waitKey(1)
            if key == 27:  # ESC
                break
            number = gesture_id

            _, img = cap.read()
            img = cv.flip(img, 1)
            debug_image = copy.deepcopy(img)
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            results = hands.process(img)
            mylmList = []
            myhand_typeList = []
            
            if results.multi_hand_landmarks:
                htrack = hd()
                mylmList, myhand_typeList = htrack.findHands(results.multi_hand_landmarks, results.multi_handedness, img)
                for lmlist, hand_type in zip(mylmList, myhand_typeList):
                    if hand_type == 'Left':
                        self.left_fingers = htrack.fingersUp(lmlist, hand_type)
                        if self.left_fingers == [1, 1, 0, 0, 1]:
                            self.type = 0
                            self.activation_textCv = "Gesture Recognition Deactive"
                            
                        if self.left_fingers == [1, 0, 0, 0, 1]:
                            self.type = 1
                            self.activation_textCv = "Gesture Recognition Active"
                    
                
                if len(results.multi_hand_landmarks) == 2 and self.type == 1 and mode == 0:
                    if self.left_fingers == [1, 0, 0, 0, 0]:
                        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                            if handedness.classification[0].label == 'Right':
                                # Landmark calculation
                                landmark_list = self.calc_landmark_list(debug_image, hand_landmarks)

                                # Conversion to relative coordinates / normalized coordinates
                                pre_processed_landmark_list = self.pre_process_landmark(landmark_list)
                                
                                # if mode == 1:
                                #     queue.put(debug_image)
                                #     # Write to the dataset file
                                #     self.logging_csv(number, mode, pre_processed_landmark_list, new_points_csv_path, key)

                                # if mode == 0:
                                loaded_model = self.load_model(model_name)
                                predict = loaded_model.predict(np.array([pre_processed_landmark_list])) 
                                hand_sign_id = predict[0]
                                
                                
                                # print(predict, "predict from process_new")
                                if temp_hand_sign_id == hand_sign_id:
                                    iterate = False
                                    count += 1
                                    # print(count)
                                else:
                                    iterate = True
                                    temp_hand_sign_id = hand_sign_id
                                    count = 0
                                    

                                if count > 15:
                                    count = 0
                                    iterate = True

                                if iterate == True:
                                    queue.put(hand_sign_id)
                                    self.gesture_label = keypoint_classifier_labels.keypoint_classifier_labels(hand_sign_id)
                                    self.keybind_text = keybinding.keybinding(hand_sign_id, profile_id)
                                    

                                    # print(hand_sign_id)
                                    # self.keybinding(hand_sign_id)
                                    
                        
                    if self.left_fingers == [0, 0, 0, 0, 0]:
                        iterate = True
                        temp_hand_sign_id = -1
                        count = 0
                        # print("LEFT CLOSED")

                else:
                    
                    if mode == 0: 
                        iterate = True
                        temp_hand_sign_id = -1
                        count = 0
                    else:
                        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                            if handedness.classification[0].label == 'Right':
                                
                                text2 = "Right hand detected."
                                cv.putText(debug_image, text2, (25, 25), self.font, 0.5, (0, 255, 0), 2)
                                # Landmark calculation
                                landmark_list = self.calc_landmark_list(debug_image, hand_landmarks)

                                # Conversion to relative coordinates / normalized coordinates
                                pre_processed_landmark_list = self.pre_process_landmark(landmark_list)
                                
                                # queue.put(debug_image)
                                # Write to the dataset file

                                
                                text1 = "Press or hold q to capture frames"
                                cv.putText(debug_image, text1, (170, 450), self.font, 0.5, (0, 255, 0), 2)

                                self.logging_csv(number, mode, pre_processed_landmark_list, new_points_csv_path, key)
                            if len(results.multi_hand_landmarks) < 2:
                                if handedness.classification[0].label == 'Left':
                                    text2 = "Only right hand gestures are trainable"
                                    cv.putText(debug_image, text2, (25, 25), self.font, 0.5, (0, 255, 0), 2)
                                    
                        
                # htrack = hd
                # mylmList, myhand_typeList = htrack.findHands(results.multi_hand_landmarks, results.multi_handedness, img)
                # print(mylmList)
                # # print(len(mylmList))
                # print(myhand_typeList)

                # print(results.multi_handedness)
                # print(len(results.multi_hand_landmarks))
                # # count = 0
                # # for handLms in results.multi_hand_landmarks:
                # #     ## lmList
                # #     count += 1
                # #     print(count)
                    
                # # #     for i, lm in enumerate(handLms.landmark):
                # # #         print(i, lm)
                # # # #         px, py, pz = int(lm.x), int(lm.y), int(lm.z)
                # # # #         mylmList.append([px, py, pz])
                # # # # print(mylmList)
            
            else:
                text2 = "No hands detected"
                cv.putText(debug_image, text2, (25, 25), self.font, 0.5, (0, 255, 0), 2)

            if mode == 0:
                cv.putText(debug_image, self.activation_textCv, (400, 25), self.font, 0.5, (0, 255, 0), 2)
                cv.putText(debug_image, "Gesture: " + self.gesture_label + "  Action: " + self.keybind_text, (170, 450), self.font, 0.5, (0, 255, 0), 2)

            if cam_show:
                if mode==1:
                    cv.putText(debug_image, "Frames Captured: " + str(self.keypoints_count), (450, 25), self.font, 0.5, (0, 255, 0), 2)
                cv.imshow("Image", debug_image)
            # key = cv.waitKey(1)
            # if key == 27:
            #     break

        if mode == 1:   
            self.queue.put(self.keypoints_count) 
        cap.release()   
        cv.destroyAllWindows() 

    # def keybinding(self, hand_sign_id):
    #     gesture_id = int(hand_sign_id)
    #     print(gesture_id)
    #     db_connector.connect()
    #     result = db_connector.execute("select key_string from KeyboardBind where gesture_id = ?", (gesture_id, ))
    #     if len(result):
    #         action = result[0][0]
    #         action = action.split(" ")
    #         print(action)
    #         pg.hotkey(action)
    #     else:
    #         print("query returned empty")

    
    def load_model(self, file_path):
        from knn_classifier import kNNClassifier
        kNN_model = joblib.load(file_path)
        return kNN_model


    def calc_landmark_list(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point


    def pre_process_landmark(self, landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(
            itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list

    def logging_csv(self, number, mode, landmark_list, new_points_csv_path, key):
        if key == 113:
            self.keypoints_count += 1
            csv_path = new_points_csv_path
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([number, *landmark_list])
        return


    # def select_mode(self, new_label_csv_path):
    #     number = -1

    #     csv_file_path = new_label_csv_path  # Replace 'your_file.csv' with the path to your CSV file

    #     # Open the CSV file
    #     with open(csv_file_path, 'r') as file:
    #         # Create a CSV reader object
    #         csv_reader = csv.reader(file)

    #         # Use the len() function to get the number of items (rows) in the CSV file
    #         number = len(list(csv_reader))

    #     return number
    
    # def read_csv(self, file_path):
    #     data = []
    #     with open(file_path, 'r') as file:
    #         reader = csv.reader(file)
    #         for row in reader:
    #             data.append(row[0])  # Assuming each row has only one element in keyboard.csv
    #     return data
    

if __name__ == '__main__':
    program = process.process()
