from db_sqlite3 import db_connector

class keypoint_classifier_labels:
    @staticmethod
    def keypoint_classifier_labels(hand_sign_id):
        db_connector.connect()
        query = "select gesture_name from Gesture where gesture_id = ?"

        parameter = (int(hand_sign_id),)
        result = db_connector.execute(query, parameter)
        db_connector.close()
        return result[0][0]