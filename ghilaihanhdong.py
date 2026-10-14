
from pynput import mouse, keyboard
import pyautogui
import time
import threading

actions = []
recording = False
playing = False
last_time = 0

stop_event = threading.Event()


# ===================== GHI CHUỘT =====================

def on_click(x, y, button, pressed):
    global last_time

    if not recording or not pressed:
        return

    now = time.time()
    delay = now - last_time
    last_time = now

    actions.append(("click", button, x, y, delay))
    print(f"Đã ghi {button} tại ({x}, {y})")


# ===================== PHÁT LẠI =====================

def replay():
    global playing

    print("▶ Bắt đầu phát sau 3 giây...")
    print("Nhấn F9 để dừng.")

    if stop_event.wait(3):
        return

    while playing:
        if not actions:
            playing = False
            break

        for action in actions:
            if not playing:
                break

            if action[0] == "click":
                _, button, x, y, delay = action

                if stop_event.wait(delay):
                    break

                if button == mouse.Button.left:
                    pyautogui.click(x, y, button="left")

                elif button == mouse.Button.right:
                    pyautogui.click(x, y, button="right")

                elif button == mouse.Button.middle:
                    pyautogui.click(x, y, button="middle")

            elif action[0] == "key":
                _, key_name, delay = action

                if stop_event.wait(delay):
                    break

                special_keys = {
                    "Key.enter": "enter",
                    "Key.space": "space",
                    "Key.backspace": "backspace",
                    "Key.tab": "tab",
                    "Key.esc": "esc",
                    "Key.delete": "delete",
                    "Key.up": "up",
                    "Key.down": "down",
                    "Key.left": "left",
                    "Key.right": "right",
                    "Key.home": "home",
                    "Key.end": "end",
                    "Key.page_up": "pageup",
                    "Key.page_down": "pagedown"
                }

                if key_name in special_keys:
                    pyautogui.press(special_keys[key_name])

                elif key_name.startswith("Key.f"):
                    pyautogui.press(key_name.replace("Key.", ""))

                elif len(key_name) == 1:
                    pyautogui.write(key_name)

        if not playing:
            break

    playing = False
    print("■ Đã dừng phát.")


# ===================== BÀN PHÍM =====================

def on_press(key):
    global recording, playing, last_time

    # F8: Bắt đầu ghi mới
    if key == keyboard.Key.f8:
        if recording:
            return

        if playing:
            playing = False
            stop_event.set()

        actions.clear()
        recording = True
        last_time = time.time()

        print("▶ Bắt đầu ghi...")
        return

    # F9: Dừng ghi / bật tắt phát lặp
    if key == keyboard.Key.f9:

        # Đang ghi thì dừng và phát
        if recording:
            recording = False
            print("■ Đã dừng ghi.")

            playing = True
            stop_event.clear()

            threading.Thread(
                target=replay,
                daemon=True
            ).start()

        # Đang phát thì dừng
        elif playing:
            playing = False
            stop_event.set()

        # Đã dừng thì phát lại
        elif actions:
            playing = True
            stop_event.clear()

            threading.Thread(
                target=replay,
                daemon=True
            ).start()

        return

    # Không ghi thì bỏ qua
    if not recording:
        return

    # Ghi phím và thời gian
    now = time.time()
    delay = now - last_time
    last_time = now

    try:
        actions.append(("key", key.char, delay))
        print(f"Đã ghi phím {key.char}")

    except AttributeError:
        actions.append(("key", str(key), delay))
        print(f"Đã ghi phím {key}")


# ===================== KHỞI ĐỘNG =====================

mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

print("F8 = Bắt đầu ghi")
print("F9 = Dừng ghi / phát lặp / dừng phát")

keyboard_listener.join()