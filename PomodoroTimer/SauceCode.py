import FreeSimpleGUI as sg
import time
import winsound
import os

sg.theme('DarkGrey9')
COLOR_WORK = '#4A90E2'
COLOR_REST = '#A066CB'
COLOR_BG = sg.theme_background_color()
COLOR_TXT = '#FFFFFF'

alarms = [f"Alarm{i:02d}.wav" for i in range(1, 11)]

state = {
    "LOOP": 1, "WORK": 25, "REST": 5,
    "running": False, "paused": False, "is_work": True,
    "current_loop": 1, "time_left": 0, "total_sec": 0,
    "previewing": False
}

def draw_timer_circle(graph, ratio, time_str, status, loop_info):
    graph.erase()
    color = COLOR_WORK if state["is_work"] else COLOR_REST
    graph.draw_circle((125, 125), 100, line_color='#333333', line_width=2)
    if ratio > 0:
        graph.draw_arc((25, 25), (225, 225), 360 * ratio, 90, style='arc', arc_color=color, line_width=8)
    graph.draw_text(loop_info, (125, 180), color='#AAAAAA', font=("Arial", 10))
    graph.draw_text(status, (125, 155), color=color, font=("Arial", 12, "bold"))
    graph.draw_text(time_str, (125, 110), color='white', font=("Consolas", 36, "bold"))

def btn_mini(text, key):
    """余白を最小限にしたボタン"""
    return sg.Button(text, key=key, border_width=0, font=("Arial", 12), 
                     button_color=(COLOR_TXT, COLOR_BG), mouseover_colors=(COLOR_BG, COLOR_BG), pad=(0, 0))

layout_settings = [
    [sg.VPush()],
    [sg.Text("Loop", font=("Arial", 10), pad=((0,0),(0,10)))],
    [btn_mini("◀", "-LOOP_DN-"), 
     sg.Text(str(state["LOOP"]), key="-LOOP_VAL-", font=("Arial", 20, "bold"), size=(3, 1), justification='c'), 
     btn_mini("▶", "-LOOP_UP-")],

    [sg.Text("", size=(1, 1))],

    [sg.Column([
        [sg.Text("Work", font=("Arial", 9))],
        [btn_mini("▲", "-WORK_UP-")],
        [sg.Text(str(state["WORK"]), key="-WORK_VAL-", font=("Arial", 18, "bold"), size=(2, 1), justification='c')],
        [btn_mini("▼", "-WORK_DN-")]
    ], element_justification='c', pad=(20, 0)),
     sg.Column([
        [sg.Text("Rest", font=("Arial", 9))],
        [btn_mini("▲", "-REST_UP-")],
        [sg.Text(str(state["REST"]), key="-REST_VAL-", font=("Arial", 18, "bold"), size=(2, 1), justification='c')],
        [btn_mini("▼", "-REST_DN-")]
    ], element_justification='c', pad=(20, 0))],

    [sg.Text("", size=(1, 2))],

    [sg.Combo(alarms, default_value="Alarm01.wav", key="-ALARM-", readonly=True, size=(12, 1), font=("Arial", 10)),
     sg.Button("♫", key="-PREVIEW-", border_width=0, button_color=("white", COLOR_BG), 
               mouseover_colors=(COLOR_BG, COLOR_BG), font=("Arial", 14))],

    [sg.Button("▶", key="-START-", font=("Arial", 40), button_color=(COLOR_WORK, COLOR_BG), 
               mouseover_colors=(COLOR_BG, COLOR_BG), border_width=0, pad=(0, 20))],
    [sg.VPush()]
]

layout_timer = [
    [sg.VPush()],
    [sg.Graph((250, 250), (0, 0), (250, 250), key="-GRAPH-", background_color=COLOR_BG)],
    [sg.Button("■", key="-STOP-", border_width=0, size=(2, 1), button_color=(COLOR_TXT, "#333333")),
     sg.Button("⏸", key="-PAUSE-", border_width=0, size=(2, 1), button_color=(COLOR_TXT, "#333333")),
     sg.Button("⏭", key="-SKIP-", border_width=0, size=(2, 1), button_color=(COLOR_TXT, "#333333"))],
    [sg.VPush()]
]

layout = [[
    sg.Column(layout_settings, key="-COL_SET-", element_justification='c', size=(300, 450)),
    sg.Column(layout_timer, key="-COL_TIMER-", visible=False, element_justification='c', size=(300, 450))
]]

window = sg.Window("Pomodoro", layout, finalize=True, keep_on_top=True, element_padding=(0,0))

end_time = 0

while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED: break

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
            path = os.path.join(r"C:\Windows\Media", values["-ALARM-"])
            if os.path.exists(path):
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                state["previewing"] = True

    if event == "-START-":
        state.update({"running": True, "paused": False, "is_work": True, "current_loop": 1})
        state["time_left"] = state["total_sec"] = state["WORK"] * 60
        end_time = time.time() + state["time_left"]
        window["-COL_SET-"].update(visible=False)
        window["-COL_TIMER-"].update(visible=True)

    if event == "-STOP-":
        state["running"] = False
        window["-COL_TIMER-"].update(visible=False)
        window["-COL_SET-"].update(visible=True)
        winsound.PlaySound(None, winsound.SND_PURGE)

    if event == "-PAUSE-":
        state["paused"] = not state["paused"]
        window["-PAUSE-"].update("▶" if state["paused"] else "⏸")
        if not state["paused"]: end_time = time.time() + state["time_left"]

    if event == "-SKIP-":
        state["time_left"] = 0

    if state["running"] and not state["paused"]:
        current_ts = time.time()
        state["time_left"] = int(end_time - current_ts)

        ratio = max(0, state["time_left"] / state["total_sec"])
        m, s = divmod(max(0, state["time_left"]), 60)
        draw_timer_circle(window["-GRAPH-"], ratio, f"{m:02d}:{s:02d}", 
                          "WORK" if state["is_work"] else "REST", 
                          f"{state['current_loop']} / {state['LOOP']}")

        if state["time_left"] <= 0:
            path = os.path.join(r"C:\Windows\Media", values["-ALARM-"])
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

            if state["is_work"]:
                state["is_work"] = False
                state["time_left"] = state["total_sec"] = state["REST"] * 60
            else:
                state["current_loop"] += 1
                if state["current_loop"] > state["LOOP"]:
                    state["running"] = False
                    sg.popup_no_buttons("Complete!", auto_close=True, auto_close_duration=2)
                    window["-STOP-"].click()
                    continue
                state["is_work"] = True
                state["time_left"] = state["total_sec"] = state["WORK"] * 60

            end_time = time.time() + state["time_left"]

window.close()