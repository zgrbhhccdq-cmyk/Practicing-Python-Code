import FreeSimpleGUI as sg
import time
import winsound
import os

sg.theme('DarkGrey9')

alarms = [f"Alarm{i:02d}.wav" for i in range(1, 11)]

settings_layout = [
    [sg.Push(), sg.Text("Loop", font=("Meiryo", 12)), sg.Push()],
    [sg.Push(), 
     sg.Button("◀", key="-LOOP_DEC-", button_color=(sg.theme_text_color(), sg.theme_background_color()), border_width=0),
     sg.Text("1", key="-LOOP-", font=("Meiryo", 16), size=(3, 1), justification='c'),
     sg.Button("▶", key="-LOOP_INC-", button_color=(sg.theme_text_color(), sg.theme_background_color()), border_width=0), 
     sg.Push()],
    [sg.Text("Work (min)", font=("Meiryo", 10), size=(10, 1), justification='c'), 
     sg.Text("Rest (min)", font=("Meiryo", 10), size=(10, 1), justification='c')],
    [sg.Spin([i for i in range(1, 100)], initial_value=10, key="-WORK-", font=("Meiryo", 16), size=(4, 1), readonly=True),
     sg.Spin([i for i in range(1, 100)], initial_value=2, key="-BREAK-", font=("Meiryo", 16), size=(4, 1), readonly=True)],
    [sg.Frame('', [
        [sg.Text("♪", font=("Meiryo", 10)), 
         sg.Combo(alarms, default_value="Alarm01.wav", key="-ALARM-", readonly=True, size=(12, 1), font=("Meiryo", 10))]
    ], border_width=0, element_justification='c')],
    [sg.Text("")],
    [sg.Push(), sg.Button("▶", key="-START-", font=("Meiryo", 20), button_color=("white", "#4A90E2"), border_width=0, size=(5, 1)), sg.Push()]
]

timer_layout = [
    [sg.Push(), sg.Text("1/1", key="-PROGRESS-", font=("Meiryo", 12)), sg.Push()],
    [sg.Push(), sg.Text("Working", key="-STATUS-", font=("Meiryo", 14)), sg.Push()],
    [sg.Push(), sg.Text("00:00:00", key="-TIME-", font=("Meiryo", 36), text_color="#4A90E2"), sg.Push()],
    [sg.Push(),
     sg.Button("■", key="-STOP-", font=("Meiryo", 12), size=(3, 1)),
     sg.Button("⏸", key="-PAUSE-", font=("Meiryo", 12), size=(3, 1)),
     sg.Button("⏭", key="-SKIP-", font=("Meiryo", 12), size=(3, 1)),
     sg.Push()]
]

layout = [
    [sg.Column(settings_layout, key="-COL_SET-", element_justification='c'),
     sg.Column(timer_layout, key="-COL_TIMER-", visible=False, element_justification='c')]
]

window = sg.Window("PomodoroTimer", layout, resizable=False, margins=(30, 20), finalize=True)

loop_count = 1
total_loops = 1
current_loop = 1
is_running = False
is_paused = False
is_working = True

time_left = 0
work_time_sec = 0
break_time_sec = 0
end_time = 0
selected_alarm = ""

def format_time(seconds):
    """秒数を HH:MM:SS にフォーマットする"""
    if seconds < 0: seconds = 0
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def play_alarm(alarm_name):
    """Windowsのメディアフォルダからアラームを非同期で再生する"""
    wav_path = os.path.join(r"C:\Windows\Media", alarm_name)
    if os.path.exists(wav_path):
        winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

def stop_timer():
    """タイマーを停止して設定画面に戻る"""
    global is_running
    is_running = False
    window["-COL_TIMER-"].update(visible=False)
    window["-COL_SET-"].update(visible=True)
    winsound.PlaySound(None, winsound.SND_PURGE)

while True:
    event, values = window.read(timeout=100)

    if event == sg.WIN_CLOSED:
        break

    if event == "-LOOP_DEC-":
        if loop_count > 1:
            loop_count -= 1
            window["-LOOP-"].update(str(loop_count))
    elif event == "-LOOP_INC-":
        if loop_count < 99:
            loop_count += 1
            window["-LOOP-"].update(str(loop_count))

    elif event == "-START-":
        total_loops = loop_count
        current_loop = 1
        work_time_sec = int(values["-WORK-"]) * 60
        break_time_sec = int(values["-BREAK-"]) * 60
        selected_alarm = values["-ALARM-"]

        is_working = True
        is_running = True
        is_paused = False
        time_left = work_time_sec
        end_time = time.time() + time_left

        window["-COL_SET-"].update(visible=False)
        window["-COL_TIMER-"].update(visible=True)
        window["-PROGRESS-"].update(f"{current_loop}/{total_loops}")
        window["-STATUS-"].update("作業中", text_color="#4A90E2")
        window["-PAUSE-"].update("⏸")
        window["-TIME-"].update(format_time(time_left))

    elif event == "-STOP-":
        stop_timer()

    elif event == "-PAUSE-":
        if is_paused:
            end_time = time.time() + time_left
            is_paused = False
            window["-PAUSE-"].update("⏸")
        else:
            is_paused = True
            window["-PAUSE-"].update("▶")

    elif event == "-SKIP-":
        end_time = time.time()

    if is_running and not is_paused:
        current_time = time.time()
        time_left = int(end_time - current_time)

        if time_left <= 0:
            play_alarm(selected_alarm)

            if is_working:
                is_working = False
                time_left = break_time_sec
                end_time = time.time() + time_left
                window["-STATUS-"].update("休憩中", text_color="#4CAF50")
            else:
                current_loop += 1
                if current_loop > total_loops:
                    stop_timer()
                    continue
                else:
                    is_working = True
                    time_left = work_time_sec
                    end_time = time.time() + time_left
                    window["-PROGRESS-"].update(f"{current_loop}/{total_loops}")
                    window["-STATUS-"].update("作業中", text_color="#4A90E2")

        window["-TIME-"].update(format_time(time_left))

window.close()
