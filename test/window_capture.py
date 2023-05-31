#用于实时截取窗口画面

import win32gui
import cv2
import numpy as np
from PIL import ImageGrab
from pynput import keyboard

hwnd_title = dict() #创建字典保存窗口的句柄与名称映射关系
def get_all_hwnd(hwnd, mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

win32gui.EnumWindows(get_all_hwnd, 0)

for h, t in hwnd_title.items():
    if t!= "":
        print(h, t)

hwnd = win32gui.FindWindow(None, 'Apex Legends')
while True:
    x_start, y_start, x_end, y_end = win32gui.GetWindowRect(hwnd)
    box = (x_start, y_start, x_end, y_end)
    image = ImageGrab.grab(box)
    img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    cv2.imshow('Img', img)
    cv2.waitKey(1)
