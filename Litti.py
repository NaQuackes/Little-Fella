import random
import tkinter as tk
import os
import sys

# --- Helper to load resources ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

impath = resource_path('image') + os.sep

# --- Tkinter setup ---
window = tk.Tk()
window.overrideredirect(True)
window.config(bg="red")
window.wm_attributes('-transparentcolor', 'red')

# Pet window size
PET_WIDTH = 290
PET_HEIGHT = 461

# Get screen dimensions for border detection
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# --- Global state ---
state = {
    "x": 500.0,
    "y": 0.0,
    "vy": 0.0,
    "cycle": 0,
    "check": 0,
    "event_number": random.choice([0, 1, 2]),
    "is_dragging": False,
    "ground_y": screen_height - 200,  # 60 px from bottom
    "anim_counter": 0,
    "drag_cycle": 0,
    "drag_counter": 0
}
drag_data = {"x": 0, "y": 0}

GRAVITY = 0.5
UPDATE_INTERVAL = 40        # ~50 FPS
ANIMATION_SPEED = 7         # slower idle/walk animation
DRAG_ANIMATION_SPEED = 5    # slower drag animation

window.geometry(f"{PET_WIDTH}x{PET_HEIGHT}+{int(state['x'])}+{int(state['y'])}")

# --- Load GIFs ---
print("Loading GIFs...")
idle = [tk.PhotoImage(file=impath + 'idle.gif', format='gif -index %i' % i) for i in range(20)]
walk_left = [tk.PhotoImage(file=impath + 'left.gif', format='gif -index %i' % i) for i in range(9)]
walk_right = [tk.PhotoImage(file=impath + 'right.gif', format='gif -index %i' % i) for i in range(9)]
drag = [tk.PhotoImage(file=impath + 'drag.gif', format='gif -index %i' % i) for i in range(1)]
print("GIFs loaded!")

label = tk.Label(window, bd=0, bg="red")
label.place(x=0, y=0)

# --- Main update loop ---
def update():
    if state["is_dragging"]:
        window.after(UPDATE_INTERVAL, update)
        return

    # Gravity
    if state["y"] < state["ground_y"]:
        state["vy"] += GRAVITY
        state["y"] += state["vy"]
        if state["y"] > state["ground_y"]:
            state["y"] = state["ground_y"]
            state["vy"] = 0.0
    else:
        state["vy"] = 0.0

    # Horizontal movement
    if state["check"] == 0:
        frames = idle
    elif state["check"] == 1:
        frames = walk_left
        state["x"] -= 4.0
    elif state["check"] == 2:
        frames = walk_right
        state["x"] += 4.0

    # Slow animation
    state["anim_counter"] += 1
    if state["anim_counter"] >= ANIMATION_SPEED:
        state["cycle"] = (state["cycle"] + 1) % len(frames)
        state["anim_counter"] = 0
        label.configure(image=frames[state["cycle"]])

    # Pick new action at start of cycle
    if state["cycle"] == 0:
        state["event_number"] = random.choice([0, 1, 2])
        state["check"] = state["event_number"]

    # Clamp to screen boundaries
    state["x"] = max(0, min(state["x"], screen_width - PET_WIDTH))
    state["y"] = max(0, min(state["y"], state["ground_y"]))

    window.geometry(f'{PET_WIDTH}x{PET_HEIGHT}+{int(state["x"])}+{int(state["y"])}')
    window.after(UPDATE_INTERVAL, update)

# --- Drag animation ---
def play_drag_animation(drag_cycle=0):
    if not state["is_dragging"]:
        return
    frame = drag[drag_cycle]
    label.configure(image=frame)
    drag_cycle = (drag_cycle + 1) % len(drag)
    window.after(100, play_drag_animation, drag_cycle)

# --- Mouse drag ---
def start_drag(event):
    state["is_dragging"] = True
    drag_data["x"] = event.x
    drag_data["y"] = event.y
    play_drag_animation(0)

def on_drag(event):
    new_x = window.winfo_x() + event.x - drag_data["x"]
    new_y = window.winfo_y() + event.y - drag_data["y"]
    state["x"] = new_x
    state["y"] = new_y
    window.geometry(f'{PET_WIDTH}x{PET_HEIGHT}+{int(new_x)}+{int(new_y)}')

def stop_drag(event):
    state["is_dragging"] = False
    state["vy"] = 0
    state["cycle"] = 0
    state["event_number"] = random.choice([0, 1, 2])
    state["check"] = state["event_number"]
    window.after(1, update)

# --- Bind dragging ---
label.bind("<ButtonPress-1>", start_drag)
label.bind("<B1-Motion>", on_drag)
label.bind("<ButtonRelease-1>", stop_drag)

# --- Start main loop ---
window.after(UPDATE_INTERVAL, update)
print("Mainloop starting...")
window.mainloop()
