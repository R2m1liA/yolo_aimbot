import time

from Capturer import Capturer, Detector, Timer, Monitor
import cv2
import ctypes
import multiprocessing
from multiprocessing import Process
import pynput
from pynput.mouse import Button
from pynput.keyboard import Key, Listener
import winsound
import win32gui
import win32con

ads = 'ads'
size = 'size'
stop = 'stop'
lock = 'lock'
show = 'show'
head = 'head'
left = 'left'
right = 'right'
title = 'title'
region = 'region'
center = 'center'
radius = 'radius'
weights = 'weights'
confidence = 'confidence'

init = {
    title: 'Apex Legends',  # 游戏窗体标题
    weights: 'apex_v8.pt',  # 模型权重文件
    confidence: 0.5,  # 置信度, 低于该值的认为是干扰
    size: 320,  # 目标检测范围, 屏幕中心 size*size 大小
    radius: 120,  # 瞄准生效半径
    ads: 0.7,  # 移动倍数
    center: None,  # 屏幕中心点
    region: None,  # 截图范围
    stop: False,  # 退出, End
    lock: False,  # 锁定, Shift
    show: False,  # 显示, Down
    head: False,  # 瞄头, Up
    left: False,  # 左键锁, Left
    right: False,  # 右键锁, Right
}


def game():
    # 判断是否为游戏窗口
    return init[title] == win32gui.GetWindowText(win32gui.GetForegroundWindow())


def mouse(data):
    # 鼠标监听
    def down(button, pressed):
        if not game():
            return
        if button == Button.left and data[left]:
            data[lock] = pressed
        if button == Button.right and data[right]:
            data[lock] = pressed

    with pynput.mouse.Listener(on_click=down) as m:
        m.join()


def keyboard(data):
    # 键盘监听
    def press(key):
        if not game():
            return
        if key == Key.shift:
            data[lock] = True

    def release(key):
        if key == Key.end:
            # 结束程序
            data[stop] = True
            winsound.Beep(400, 200)
            return False
        if not game():
            return
        if key == Key.shift:
            data[lock] = False
        elif key == Key.up:
            data[head] = not data[head]
            winsound.Beep(800 if data[head] else 400, 200)
        elif key == Key.down:
            data[show] = not data[show]
            winsound.Beep(800 if data[show] else 400, 200)
        elif key == Key.left:
            data[left] = not data[left]
            winsound.Beep(800 if data[left] else 400, 200)

    with Listener(on_release=release, on_press=press) as k:
        k.join()


def loop(data):
    # 主循环，负责截图、检测、瞄准
    capturer = Capturer(data[title], data[region])
    detector = Detector(data[weights])
    winsound.Beep(800, 200)

    # 加载罗技驱动
    try:
        import os
        root = os.path.abspath(os.path.dirname(__file__))
        driver = ctypes.CDLL(f'{root}/logitech.driver.dll')
        ok = driver.device_open() == 1  # 该驱动每个进程可打开一个实例
        if not ok:
            print('初始化失败，未找到罗技驱动')
    except FileNotFoundError:
        print('初始化失败，缺少DLL文件')

    # 移动鼠标
    def move(x: int, y: int):
        if (x == 0) & (y == 0):
            return
        driver.moveR(x, y, True)

    # 判断目标是否在瞄准范围内
    def inner(point):
        a, b = data[center]
        x, y = point
        return (x - a) ** 2 + (y - b) ** 2 <= data[radius] ** 2

    # 获取目标坐标
    def follow(aims):
        if len(aims) == 0:
            return None

        targets = []
        for index, clazz, conf, sc, gc, sr, gr in aims:
            if conf < data[confidence]:  # 置信度过滤
                continue
            _, _, _, height = sr
            sx, sy = sc
            gx, gy = gc
            differ = height // 3
            newSc = sx, sy - height // 2 + differ
            newGc = gx, gy - height // 2 + differ
            targets.append((index, clazz, conf, newSc, newGc, sr, gr))
        if len(targets) == 0:
            return None

        cx, cy = data[center]
        index = 0
        minimum = 0
        for i, item in enumerate(targets):
            index, clazz, conf, sc, gc, sr, gr = item
            sx, sy = sc
            distance = (sx - cx) ** 2 + (sy - cy) ** 2
            if minimum == 0 or distance < minimum:
                minimum = distance
                index = i
        return targets[index]

    text = 'Realtime Detect'


    while True:
        if not game():
            print('未检测到标题为', data[title], '的窗口')
            time.sleep(1)
        try:
            # t1 = time.perf_counter_ns()
            img = capturer.get_screen(data[region])
            # t2 = time.perf_counter_ns()
            aims, img = detector.detect(image=img, show=data[show], head=data[head])
            # t3 = time.perf_counter_ns()
            aims = detector.convert(aims=aims, region=data[region])

            # 获取目标坐标
            target = follow(aims)
            # 自动瞄准
            if data[lock] and target:
                index, clazz, conf, sc, gc, sr, gr = target
                if inner(sc):
                    cx, cy = data[center]
                    sx, sy = sc
                    x = sx - cx
                    y = sy - cy
                    ax = int(x * data[ads])
                    ay = int(y * data[ads])
                    move(ax, ay)
            # 显示检测窗口
            if data[show] and img is not None:
                if target:
                    # 绘制准心到目标的连线
                    index, clazz, conf, sc, gc, sr, gr = target
                    cv2.circle(img, gc, 2, (0, 0, 0), 2)
                    r = data[size] // 2
                    cv2.line(img, gc, (r, r), (255, 255, 0), 2)
                """
                # 记录转换时间，用于测试性能
                cv2.putText(img, f'{Timer.cost(t3 - t1)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(img, f'{Timer.cost(t2 - t1)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(img, f'{Timer.cost(t3 - t2)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                """
                # 显示并置顶检测窗口
                cv2.namedWindow(text, cv2.WINDOW_AUTOSIZE)
                cv2.imshow(text, img)
                win32gui.SetWindowPos(win32gui.FindWindow(None, text), win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                cv2.waitKey(1)
            if not data[show]:
                cv2.destroyAllWindows()
        except:
            pass


if __name__ == '__main__':
    multiprocessing.freeze_support()
    manager = multiprocessing.Manager()
    data = manager.dict()
    data.update(init)
    # 初始化数据
    data[center] = Monitor.resolution.center()
    c1, c2 = data[center]
    data[region] = c1 - data[size] // 2, c2 - data[size] // 2, data[size], data[size]
    # 创建进程
    pMouse = Process(target=mouse, args=(data,), name='Mouse')
    pKeyboard = Process(target=keyboard, args=(data,), name='Keyboard')
    pLoop = Process(target=loop, args=(data,), name='Loop')
    # 启动进程
    pMouse.start()
    pKeyboard.start()
    pLoop.start()
    pKeyboard.join()
    pMouse.terminate()
