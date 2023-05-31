# 自动截屏，用于获取训练集

import time
import os
import datetime
import win32gui, win32ui, win32con, win32api


def window_capture(filename):
    hwnd = 0  # 窗口编号，0为当前活跃窗口
    hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC(Device Conte)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口DC获取mfcDC
    saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建bitmap准备保存图片

    MoniterDev = win32api.EnumDisplayMonitors(None, None)   # 获取监视器信息
    weight = MoniterDev[0][2][2]    # 当前监视器最大宽度
    height = MoniterDev[0][2][3]    # 当前监视器最大高度

    saveBitMap.CreateCompatibleBitmap(mfcDC, weight, height)    #为bitmap开辟空间
    saveDC.SelectObject(saveBitMap) # 高度saveDC,将截图保存到saveBitmap中
    #截取从（0,0）到（weight，height）的图片
    saveDC.BitBlt((0, 0), (weight, height), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)

if __name__ == "__main__":
    for i in range(0, 999):
        window_capture('pic/' + time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time())) + '.jpg')
        time.sleep(2)
