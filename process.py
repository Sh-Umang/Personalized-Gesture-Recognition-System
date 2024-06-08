#process.py
import argparse
import csv
import cv2 as cv
import mediapipe as mp
import copy
import itertools
import tensorflow as tf
import numpy as np
import pickle
import joblib
import multiprocessing
from knn_classifier import kNNClassifier


from sklearn.svm import SVC
from sklearn.multiclass import OneVsOneClassifier

class process:

    @staticmethod
    def process(queue, new_points_csv_path, new_label_csv_path, model_name, _mode, cam_show):
        # Argument parsing #################################################################
        self = process

        cap_device = 0
        cap_width = 960
        cap_height = 540
        hand_mode = 1

        # Camera preparation ###############################################################
        cap = cv.VideoCapture(cap_device)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

        # Hand Detection Model load #############################################################
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode = True,
            max_num_hands = 2,
            min_detection_confidence = 0.7,
            min_tracking_confidence = 0.5,
        )

        # Read labels ###########################################################
        with open(new_label_csv_path,
                encoding='utf-8-sig') as f:
            keypoint_classifier_labels = csv.reader(f)
            keypoint_classifier_labels = [
                row[0] for row in keypoint_classifier_labels
            ]

        mode = _mode
        
        while True:

            # Process Key (ESC: end) #################################################
            key = cv.waitKey(10)
            if key == 27:  # ESC
                break
            number = self.select_mode(new_label_csv_path)

            # Camera capture #####################################################
            ret, image = cap.read()
            if not ret:
                break
            image = cv.flip(image, 1)  # Mirror display
            debug_image = copy.deepcopy(image)
            # cv.imshow('Hand Gesture Recognition', image)
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True

            
            #  ####################################################################
            if results.multi_hand_landmarks is not None:
                # for handedness in results.multi_handedness:
                #     hand = handedness.classification[0].label[0:]
                #     if hand == "Left":

                #         print(len(results.multi_handedness))
                        
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,results.multi_handedness):
                    # Landmark calculation
                    landmark_list = self.calc_landmark_list(debug_image, hand_landmarks)

                    # Conversion to relative coordinates / normalized coordinates
                    pre_processed_landmark_list = self.pre_process_landmark(landmark_list)
                    
                    if mode == 1:
                        # Write to the dataset file
                        self.logging_csv(number, mode, pre_processed_landmark_list, new_points_csv_path, key)
                    
                    if mode == 0:
                        hand = handedness.classification[0].label
                        if hand == "Left":
                            hand_mode_model = self.load_model("hand_mode.sav")
                            predict_mode = hand_mode_model.predict(np.array([pre_processed_landmark_list]))
                            hand_mode = predict_mode[0]

                        loaded_model = self.load_model(model_name)
                        predict = loaded_model.predict(np.array([pre_processed_landmark_list])) 
                        hand_sign_id = predict[0] 

                        key = keypoint_classifier_labels[hand_sign_id] 
                        queue.put(hand_sign_id)
                        # print(keypoint_classifier_labels)
            if cam_show:
                cv.imshow('Hand Gesture Recognition', debug_image)
                    
        cap.release()   
        cv.destroyAllWindows()         

    def load_model(file_path):
        from knn_classifier import kNNClassifier
        kNN_model = joblib.load(file_path)
        return kNN_model


    def calc_landmark_list(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point


    def pre_process_landmark(landmark_list):
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

    def logging_csv(number, mode, landmark_list, new_points_csv_path, key):
        if mode == 0:
            pass
        if mode == 1 and key == 113:
            csv_path = new_points_csv_path
            with open(csv_path, 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([number, *landmark_list])
        return


    def select_mode(new_label_csv_path):
        number = -1

        csv_file_path = new_label_csv_path  # Replace 'your_file.csv' with the path to your CSV file

        # Open the CSV file
        with open(csv_file_path, 'r') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # Use the len() function to get the number of items (rows) in the CSV file
            number = len(list(csv_reader))

        return number
    
    def read_csv(file_path):
        data = []
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row[0])  # Assuming each row has only one element in keyboard.csv
        return data





