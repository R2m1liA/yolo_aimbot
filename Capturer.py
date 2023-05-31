import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.yolo.utils.torch_utils import smart_inference_mode

import win32gui
from win32api import GetSystemMetrics
from win32con import SRCCOPY, SM_CXSCREEN, SM_CYSCREEN, DESKTOPHORZRES, DESKTOPVERTRES
from win32gui import GetDesktopWindow, GetWindowDC, DeleteObject, GetDC, ReleaseDC, FindWindow
from win32ui import CreateDCFromHandle, CreateBitmap
from win32print import GetDeviceCaps

from PIL import ImageGrab


class Monitor:
    class resolution:

        @staticmethod
        def show():
            # 获取屏幕分辨率
            width = GetSystemMetrics(SM_CXSCREEN)
            height = GetSystemMetrics(SM_CYSCREEN)
            return width, height

        @staticmethod
        def real():
            # 获取显示器物理分辨率
            hDC = GetDC(None)
            width = GetDeviceCaps(hDC, DESKTOPHORZRES)
            height = GetDeviceCaps(hDC, DESKTOPVERTRES)
            ReleaseDC(None, hDC)
            return width, height

        @staticmethod
        def center():
            # 获取屏幕中心点坐标
            weight, height = Monitor.resolution.real()
            return weight // 2, height // 2


class Capturer:

    def __init__(self, title: str, region: tuple, interval=60):
        self.title = title
        self.region = region
        # 设置句柄属性
        self.hwnd = None
        self.interval = interval

    # 捕获窗口并输出
    def grab(self):
        # 获取窗口句柄
        self.hwnd = FindWindow(None, self.title)
        if not self.hwnd:
            print("找不到窗口")
            exit()
        # 设置窗口置顶
        win32gui.SetForegroundWindow(self.hwnd)
        # 获取窗口截图
        dimensions = win32gui.GetWindowRect(self.hwnd)
        x_start, y_start, x_end, y_end = dimensions
        box = (x_start, y_start, x_end, y_end)
        image = ImageGrab.grab(box)
        img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        # 返回截图
        return img

    @staticmethod
    def get_screen(region):
        # 获取屏幕截图
        left, top, width, height = region
        # 获取屏幕句柄
        hWin = GetDesktopWindow()
        # 获取屏幕DC
        hWinDC = GetWindowDC(hWin)
        # 创建内存DC
        srcDC = CreateDCFromHandle(hWinDC)
        memDC = srcDC.CreateCompatibleDC()
        bmp = CreateBitmap()
        bmp.CreateCompatibleBitmap(srcDC, width, height)
        memDC.SelectObject(bmp)
        memDC.BitBlt((0, 0), (width, height), srcDC, (left, top), SRCCOPY)
        array = bmp.GetBitmapBits(True)
        DeleteObject(bmp.GetHandle())
        srcDC.DeleteDC()
        memDC.DeleteDC()
        ReleaseDC(hWin, hWinDC)
        img = np.frombuffer(array, dtype='uint8')
        img.shape = (height, width, 4)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img


class Detector:
    @smart_inference_mode()
    def __init__(self, weights):
        self.weights = weights
        # 加载模型
        self.model = YOLO(weights)
        self.names = ['body', 'head']

    @smart_inference_mode()
    def detect(self, image, show=False, head=False):
        aims = []
        img = image.copy()
        # 检测
        results = self.model(img)
        det = results[0].boxes
        # 标注检测结果
        results_plotted = results[0].plot()
        # 获取检测对象坐标等信息
        for i in range(0, len(det)):
            c = int(det[i].cls)
            xyxy = det[i].xyxy
            conf = det[i].conf
            clazz = self.names[c] if not self.weights.endswith('.engine') else str(c)
            if head:
                if c == 1:
                    aims.append((c, clazz, float(conf), xyxy.tolist()[0]))
            else:
                if c == 0:
                    aims.append((c, clazz, float(conf), xyxy.tolist()[0]))
        return aims, results_plotted if show else None

    def convert(self, aims, region):
        # 用于将截屏坐标系下的坐标xyxy转化为屏幕坐标系下的ltwhxy和截屏坐标系下的ltwhxy
        lst = []

        for item in aims:
            print(item)
            c, clazz, conf, xyxy = item
            # 屏幕坐标系下, 框的 ltwh 和 框的中心点 xy
            sl = int(region[0] + xyxy[0])
            st = int(region[1] + xyxy[1])
            sw = int(xyxy[2] - xyxy[0])
            sh = int(xyxy[3] - xyxy[1])
            sx = int(sl + sw / 2)
            sy = int(st + sh / 2)
            # 截图坐标系下, 框的 ltwh 和 框的中心点 xy
            gl = int(xyxy[0])
            gt = int(xyxy[1])
            gw = int(xyxy[2] - xyxy[0])
            gh = int(xyxy[3] - xyxy[1])
            gx = int((xyxy[0] + xyxy[2]) / 2)
            gy = int((xyxy[1] + xyxy[3]) / 2)
            # (sx, sy) 屏幕坐标系下的中心点
            # (gx, gy) 截图坐标系下的中心点
            # (sl, st, sw, sh) 屏幕坐标系下的框
            # (gl, gt, gw, gh) 截图坐标系下的框
            lst.append((c, clazz, float(conf), (sx, sy), (gx, gy), (sl, st, sw, sh), (gl, gt, gw, gh)))
        return lst



class Timer:

    @staticmethod
    def cost(interval):
        """
        转换耗时, 输入纳秒间距, 转换为合适的单位
        """
        if interval < 1000:
            return f'{interval}ns'
        elif interval < 1_000_000:
            return f'{round(interval / 1000, 3)}us'
        elif interval < 1_000_000_000:
            return f'{round(interval / 1_000_000, 3)}ms'
        else:
            return f'{round(interval / 1_000_000_000, 3)}s'