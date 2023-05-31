import win32gui
from PyQt5.QtWidgets import QApplication
import sys

hwnd_title = dict()

def get_all_hwnd(hwnd, mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

win32gui.EnumWindows(get_all_hwnd, 0)

for h, t in hwnd_title.items():
    if t != "":
        print(h, t)

hwnd = win32gui.FindWindow(None, 'autoaim – screenCut.py') # C:\Windows\system32\cmd.exe
app = QApplication(sys.argv)
screen = QApplication.primaryScreen()
img = screen.grabWindow(hwnd).toImage()
img.save("screenshot2.jpg")