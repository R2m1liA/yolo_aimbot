import pynput


def press(key):
    print(key)

def release(key):
    print(key)

with pynput.keyboard.Listener(on_press=press, on_release=release) as listener:
    listener.join()