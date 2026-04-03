import FreeSimpleGUI as sg
import time
import winsound
import os

sg.theme('DarkGrey9')
COLOR_WORK = '#4A90E2'
COLOR_REST = '#A066CB'
COLOR_BG = sg.theme_background_color()
COLOR_TXT = '#FFFFFF'

alarm_names = [f"Alarm{i:02d}" for i in range(1, 11)]

state = {
    "LOOP": 1, "WORK": 25, "REST": 5,
    "running": False, "paused": False, "is_work": True,
    "current_loop": 1, "time_left": 0, "total_sec": 0,
    "previewing": False
}

def draw_timer_circle(graph, ratio, time_str, status, loop_info):
    graph.erase()
    color = COLOR_WORK if state["is_work"] else COLOR_REST

    graph.draw_circle((125, 125), 100, line_color='#000000', line_width=10)

    if ratio > 0:
        extent = 360 * ratio
        graph.draw_arc((25, 25), (225, 225), extent, 90, style='arc', arc_color=color, line_width=10)

    graph.draw_text(loop_info, (125, 180), color='#AAAAAA', font=("Arial", 10))
    graph.draw_text(status,    (125, 155), color=color,     font=("Arial", 12, "bold"))
    graph.draw_text(time_str,  (125, 110), color='white',   font=("Consolas", 36, "bold"))

def btn_clean(text, key, font_size=12, pad=(0,0)):
    return sg.Button(text, key=key, border_width=0, font=("Arial", font_size),
                     button_color=(COLOR_TXT, COLOR_BG),
                     mouseover_colors=(COLOR_BG, COLOR_BG), pad=pad)

def stop_timer(window):
    """STOPの共通処理（直接呼び出し用）"""
    state["running"] = False
    state["previewing"] = False
    window["-PAUSE-"].update("⏸")
    window["-COL_TIMER-"].update(visible=False)
    window["-COL_SET-"].update(visible=True)
    winsound.PlaySound(None, winsound.SND_PURGE)


layout_settings = [
    [sg.VPush()],
    [sg.Text("Loop", font=("Arial", 10))],
    [btn_clean("◀", "-LOOP_DN-", pad=(10,0)),
     sg.Text(str(state["LOOP"]), key="-LOOP_VAL-", font=("Arial", 22, "bold"), size=(3, 1), justification='c'),
     btn_clean("▶", "-LOOP_UP-", pad=(10,0))],

    [sg.Text("", size=(1, 1))],

    [sg.Column([
        [sg.Text("Work", font=("Arial", 9))],
        [btn_clean("▲", "-WORK_UP-")],
        [sg.Text(str(state["WORK"]), key="-WORK_VAL-", font=("Arial", 20, "bold"), size=(2, 1), justification='c')],
        [btn_clean("▼", "-WORK_DN-")]
    ], element_justification='c', pad=(15, 0)),
     sg.Column([
        [sg.Text("Rest", font=("Arial", 9))],
        [btn_clean("▲", "-REST_UP-")],
        [sg.Text(str(state["REST"]), key="-REST_VAL-", font=("Arial", 20, "bold"), size=(2, 1), justification='c')],
        [btn_clean("▼", "-REST_DN-")]
    ], element_justification='c', pad=(15, 0))],

    [sg.Text("", size=(1, 1))],

    [btn_clean("♫", "-PREVIEW-", 16, pad=((0, 10), (0, 0))),
     sg.Combo(alarm_names, default_value="Alarm01", key="-ALARM-", readonly=True, size=(10, 1), font=("Arial", 10))],

    [btn_clean("▶", "-START-", 45, pad=(0, 15))],
    [sg.VPush()]
]

layout_timer = [
    [sg.VPush()],
    [sg.Graph((250, 250), (0, 0), (250, 250), key="-GRAPH-", background_color=COLOR_BG)],
    [btn_clean("■", "-STOP-",  18, pad=(10,0)),
     btn_clean("⏸", "-PAUSE-", 18, pad=(10,0)),
     btn_clean("⏭", "-SKIP-",  18, pad=(10,0))],
    [sg.VPush()]
]

layout = [[
    sg.Column(layout_settings, key="-COL_SET-",   element_justification='c', size=(280, 430), pad=(0,0)),
    sg.Column(layout_timer,    key="-COL_TIMER-", visible=False, element_justification='c', size=(280, 430), pad=(0,0))
]]

window = sg.Window("Pomodoro", layout, finalize=True, keep_on_top=True, element_padding=(0,0), margins=(0, 0))

end_time = 0

while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED:
        break

    updates = {
        "-LOOP_UP-": ("LOOP", 1), "-LOOP_DN-": ("LOOP", -1),
        "-WORK_UP-": ("WORK", 1), "-WORK_DN-": ("WORK", -1),
        "-REST_UP-": ("REST", 1), "-REST_DN-": ("REST", -1)
    }
    if event in updates:
        key, diff = updates[event]
        new_val = state[key] + diff
        if new_val >= 1:
            state[key] = new_val
            window[f"-{key}_VAL-"].update(str(state[key]))

    if event == "-PREVIEW-":
        if state["previewing"]:
            winsound.PlaySound(None, winsound.SND_PURGE)
            state["previewing"] = False
        else:
            path = os.path.join(r"C:\Windows\Media", values["-ALARM-"] + ".wav")
            if os.path.exists(path):
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                state["previewing"] = True

    if event == "-START-":
        state.update({"running": True, "paused": False, "is_work": True, "current_loop": 1})
        state["time_left"] = state["total_sec"] = state["WORK"] * 60
        end_time = time.time() + state["time_left"]
        window["-PAUSE-"].update("⏸")
        window["-COL_SET-"].update(visible=False)
        window["-COL_TIMER-"].update(visible=True)

    if event == "-STOP-":
        stop_timer(window)

    if event == "-PAUSE-":
        state["paused"] = not state["paused"]
        window["-PAUSE-"].update("▶" if state["paused"] else "⏸")
        if not state["paused"]:
            end_time = time.time() + state["time_left"]

    if event == "-SKIP-":
        state["time_left"] = 0
        end_time = time.time()

    if state["running"] and not state["paused"]:
        state["time_left"] = int(end_time - time.time())

        ratio = max(0, state["time_left"] / state["total_sec"])
        m, s = divmod(max(0, state["time_left"]), 60)
        draw_timer_circle(window["-GRAPH-"], ratio, f"{m:02d}:{s:02d}",
                          "WORK" if state["is_work"] else "REST",
                          f"{state['current_loop']} / {state['LOOP']}")

        if state["time_left"] <= 0:
            path = os.path.join(r"C:\Windows\Media", values["-ALARM-"] + ".wav")
            if os.path.exists(path):
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

            if state["is_work"]:
                state["is_work"] = False
                state["time_left"] = state["total_sec"] = state["REST"] * 60
            else:
                state["current_loop"] += 1
                if state["current_loop"] > state["LOOP"]:
                    sg.popup_no_buttons("Complete!", auto_close=True, auto_close_duration=2)
                    stop_timer(window)
                    continue
                state["is_work"] = True
                state["time_left"] = state["total_sec"] = state["WORK"] * 60

            end_time = time.time() + state["time_left"]

window.close()