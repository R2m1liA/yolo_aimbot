from pynput import keyboard

def on_press(key):
    if key == keyboard.Key.esc:
        print(key)
    else:
        return False


if __name__ == "__main__":
    with keyboard.Listener(on_press=on_press) as lsn:
        lsn.join()

    lsn.stop()
