import FreeSimpleGUI as sg
import time
import winsound
import os

sg.theme('DarkGrey9')
COLOR_WORK = '#4A90E2'
COLOR_REST = '#A066CB'
COLOR_BG = sg.theme_background_color()
COLOR_TXT = sg.theme_text_color()

alarms = [f"Alarm{i:02d}.wav" for i in range(1, 11)]

state = {
    "LOOP": 1, "WORK": 25, "REST": 5,
    "running": False, "paused": False, "is_work": True,
    "current_loop": 1, "time_left": 0, "total_sec": 0,
    "previewing": False
}

def draw_timer(graph, ratio, time_str, status, loop_info):
    graph.erase()
    color = COLOR_WORK if state["is_work"] else COLOR_REST
    graph.draw_circle((125, 125), 100, line_color='#333333', line_width=4)
    if ratio > 0:
        graph.draw_arc((25, 25), (225, 225), 360 * ratio, 90, style='arc', arc_color=color, line_width=10)
    graph.draw_text(loop_info, (125, 180), color='white', font=("Arial", 10))
    graph.draw_text(status, (125, 155), color=color, font=("Arial", 14, "bold"))
    graph.draw_text(time_str, (125, 110), color='white', font=("Consolas", 34, "bold"))

def v_selector(label, key):
    """Vertical selector layout: ▲ Value ▼"""
    return sg.Column([
        [sg.Text(label, font=("Arial", 9), justification='c')],
        [sg.Button("▲", key=f"-{key}_UP-", border_width=0, button_color=(COLOR_TXT, COLOR_BG))],
        [sg.Text(str(state[key]), key=f"-{key}_VAL-", font=("Arial", 18, "bold"), size=(3, 1), justification='c')],
        [sg.Button("▼", key=f"-{key}_DN-", border_width=0, button_color=(COLOR_TXT, COLOR_BG))]
    ], element_justification='c')

layout_settings = [
    [sg.VPush()],
    [v_selector("Loop", "LOOP"), v_selector("Work", "WORK"), v_selector("Rest", "REST")],
    [sg.Text("", size=(1, 1))],
    [sg.Button("♫", key="-PREVIEW-", border_width=0, font=("Arial", 12)),
     sg.Combo(alarms, default_value="Alarm01.wav", key="-ALARM-", readonly=True, size=(12, 1))],
    [sg.Button("▶", key="-START-", font=("Arial", 40), button_color=(COLOR_WORK, COLOR_BG), border_width=0)],
    [sg.VPush()]
]

layout_timer = [
    [sg.Graph((250, 250), (0, 0), (250, 250), key="-GRAPH-", background_color=COLOR_BG)],
    [sg.Button("■", key="-STOP-", border_width=0, size=(4, 1)),
     sg.Button("⏸", key="-PAUSE-", border_width=0, size=(4, 1)),
     sg.Button("⏭", key="-SKIP-", border_width=0, size=(4, 1))],
    [sg.Text("", size=(1, 1))]
]

layout = [[
    sg.Column(layout_settings, key="-COL_SET-", element_justification='c', size=(300, 400)),
    sg.Column(layout_timer, key="-COL_TIMER-", visible=False, element_justification='c', size=(300, 400))
]]

window = sg.Window("Pomodoro Timer", layout, finalize=True, no_titlebar=False, keep_on_top=True)

while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED: break

    for k in ["LOOP", "WORK", "REST"]:
        if event == f"-{k}_UP-":
            state[k] += 1
            window[f"-{k}_VAL-"].update(state[k])
        elif event == f"-{k}_DN-" and state[k] > 1:
            state[k] -= 1
            window[f"-{k}_VAL-"].update(state[k])

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
        state["running"] = True
        state["is_work"] = True
        state["current_loop"] = 1
        state["time_left"] = state["total_sec"] = state["WORK"] * 60
        end_time = time.time() + state["time_left"]
        window["-COL_SET-"].update(visible=False)
        window["-COL_TIMER-"].update(visible=True)

    if event == "-STOP-":
        state["running"] = False
        winsound.PlaySound(None, winsound.SND_PURGE)
        window["-COL_TIMER-"].update(visible=False)
        window["-COL_SET-"].update(visible=True)

    if event == "-PAUSE-":
        state["paused"] = not state["paused"]
        window["-PAUSE-"].update("▶" if state["paused"] else "⏸")
        if not state["paused"]: end_time = time.time() + state["time_left"]

    if event == "-SKIP-":
        state["time_left"] = 0

    if state["running"] and not state["paused"]:
        state["time_left"] = int(end_time - time.time())

        ratio = max(0, state["time_left"] / state["total_sec"])
        m, s = divmod(max(0, state["time_left"]), 60)
        t_str = f"{m:02d}:{s:02d}"
        status_txt = "WORK" if state["is_work"] else "REST"
        loop_txt = f"{state['current_loop']} / {state['LOOP']}"

        draw_timer(window["-GRAPH-"], ratio, t_str, status_txt, loop_txt)

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
                    sg.popup_no_buttons("Finish!", auto_close=True, auto_close_duration=3, non_blocking=True)
                    window["-STOP-"].click()
                    continue
                state["is_work"] = True
                state["time_left"] = state["total_sec"] = state["WORK"] * 60

            end_time = time.time() + state["time_left"]

window.close()