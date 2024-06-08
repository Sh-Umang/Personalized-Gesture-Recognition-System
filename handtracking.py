import math

import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self):
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, landmarks, multi_hand, img):
        h, w, c = img.shape
        my_multi_lmList = []
        my_multihand_type = []
        if landmarks:
            for handLms, handedness in zip(landmarks, multi_hand):
                ## lmList
                mylmList = []
                
                for _, lm in enumerate(handLms.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    mylmList.append([px, py])

                my_multi_lmList.append(mylmList)

                my_multihand_type.append(handedness.classification[0].label)

        return my_multi_lmList, my_multihand_type
    
    def fingersUp(self, lmlist, hand_type):
        """
        Finds how many fingers are open and returns in a list.
        Considers left and right hands separately
        :return: List of which fingers are up
        """
        fingers = []
        myHandType = hand_type
        myLmList = lmlist
        
        # Thumb
        if myHandType == "Right":
            if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers