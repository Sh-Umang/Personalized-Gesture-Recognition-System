import pyautogui as pg
import subprocess
from db_sqlite3 import db_connector

class keybinding():
    @staticmethod
    def keybinding(hand_sign_id, profile_id):
        gesture_id = int(hand_sign_id)
        print(gesture_id, "gesture id from home_tab")
        profile_id = profile_id

        print(profile_id, "profileid1 from hometab")
        db_connector.connect()
        result = db_connector.execute("select key_string from KeyboardBind where gesture_id = ? and profile_id = ?", (gesture_id, profile_id))
        print(result, "result from hometab")
        print(profile_id, "profileid2 from hometab")
        if len(result):
            action_string = result[0][0].lower()
            action = action_string.strip().split(" ")
            print(action, "action from home_tab")
            if (action[0] == "open"):
                parameter = '%' + action[1] + '%'
                query = "select path from AppPath where prog_name like ?"
                db_connector.connect()
                result = db_connector.execute(query, (parameter,))
                if result:
                    try:
                        subprocess.call(result[0][0])
                    except:
                        print("Invalid Path")
                else:
                     pass
                db_connector.close()
            elif (action[0] == "hold"):
                with pg.hold(action[1]):
                    if (action[2]=="hold"):
                        with pg.hold(action[3]):
                            for i in range (4, len(action)):
                                pg.press(action[i])
                    else:
                        for i in range (2, len(action)):
                            pg.press(action[i])
            else:
                pg.hotkey(action)
            return action_string
        else:
            print("query returned empty")
            return "No Action"