import ctypes
import time

def get_active_window_title():
    GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    GetWindowText = ctypes.windll.user32.GetWindowTextW

    hwnd = GetForegroundWindow()
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    return buff.value
# while True:
#     print(get_active_window_title())
#     soft = "give me"
#     soft = soft.split(" ")
#     print(soft)
#     time.sleep(1)
    
