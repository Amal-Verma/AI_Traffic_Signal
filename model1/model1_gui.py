IMAGE_FOLDER_PATH = "../assets/examples/images"
import os, sys, subprocess
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
sys.path.append(os.path.abspath(os.path.join('..')))
from model1.VehicleCounter import VehicleCounter

# Palette shared with the pygame simulation so the two screens look related.
BG      = "#10121a"
CARD    = "#181c26"
BORDER  = "#343b4c"
TEXT    = "#e7edf6"
MUTED   = "#8a96ac"
ACCENT  = "#7db2ff"
GREEN   = "#4ade80"
RED     = "#f87171"

DIRECTIONS = ["West", "North", "East", "South"]
PREVIEW = (200, 125)

vehicle_counter = VehicleCounter()

root = tk.Tk()
root.title("Vehicle Counter — YOLOv5 Intersection Analysis & Simulation Bridge")
root.configure(bg=BG)
root.geometry("1280x780")
root.minsize(960, 580)

image_paths = {d: None for d in DIRECTIONS}
last_counts = {d: 0 for d in DIRECTIONS}
panels = {}
labels = {}


def card(parent, direction):
    """One approach: title, image preview, upload button, results."""
    frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                     highlightthickness=1, padx=8, pady=8)

    tk.Label(frame, text=f"{direction.upper()} APPROACH", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")

    preview = tk.Label(frame, text="no image selected\nclick upload below", bg=BG, fg=MUTED,
                       font=("Segoe UI", 8), width=26, height=7)
    preview.pack(pady=(4, 4))
    panels[direction] = preview

    tk.Button(frame, text="Upload Image", command=lambda: upload_image(direction),
              bg=BORDER, fg=TEXT, activebackground=ACCENT,
              activeforeground=BG, relief="flat", padx=10, pady=3,
              font=("Segoe UI", 9, "bold"), cursor="hand2").pack(fill="x")

    result = tk.Label(frame, text="—", bg=CARD, fg=MUTED, justify="left",
                      font=("Consolas", 9))
    result.pack(anchor="w", pady=(4, 0))
    labels[direction] = result

    return frame


def upload_image(direction):
    file_path = filedialog.askopenfilename(
        initialdir=IMAGE_FOLDER_PATH,
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")])
    if not file_path:
        return
    image_paths[direction] = file_path
    image = Image.open(file_path).resize(PREVIEW, Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(image)
    panels[direction].config(image=img, text="", width=PREVIEW[0], height=PREVIEW[1])
    panels[direction].image = img  # keep reference to avoid garbage collection
    labels[direction].config(text=os.path.basename(file_path), fg=MUTED)


def count_vehicles():
    status.config(text="Running YOLOv5 detection…", fg=ACCENT)
    root.update_idletasks()

    total_weighted = 0
    counted = 0
    for direction in DIRECTIONS:
        image_path = image_paths[direction]
        if not image_path:
            labels[direction].config(text="no image", fg=MUTED)
            last_counts[direction] = 0
            continue

        result = vehicle_counter.count(image_path)
        if result is None:
            labels[direction].config(text="detection failed", fg=RED)
            last_counts[direction] = 0
            continue

        total, (car, bike, bus, truck) = result
        total_weighted += total
        last_counts[direction] = total
        counted += 1
        labels[direction].config(
            text=(f"cars     {car:>3}\n"
                  f"bikes    {bike:>3}\n"
                  f"buses    {bus:>3}\n"
                  f"trucks   {truck:>3}\n"
                  f"weighted {total:>3}"),
            fg=TEXT)

    if counted:
        status.config(
            text=f"{counted} approach(es) counted · total demand: {total_weighted} · Click 'LAUNCH SIMULATION' to run Model 2!",
            fg=GREEN)
    else:
        status.config(text="Upload at least one approach image first.", fg=MUTED)


def build_simulation_view():
    """Renders the simulation seeded with the detected demand, as an image.

    Nothing interactive is launched. main.py is run headless in snapshot mode,
    which draws one frame of the real simulation interface to a PNG, and that
    image is shown here. This demonstrates the perception output actually
    driving Model 2, without a second window to manage during a demo.
    """
    if sum(last_counts.values()) == 0:
        count_vehicles()

    counts = [last_counts[d] for d in ["West", "North", "East", "South"]]
    if sum(counts) == 0:
        status.config(text="Upload and count at least one approach first.", fg=MUTED)
        return

    status.config(text="Feeding detected demand into Model 2 and rendering…",
                  fg=ACCENT)
    root.update_idletasks()

    sim_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "model2", "Simulation", "Traffic-Simulation"))
    out_path = os.path.join(sim_dir, "data", "detected_preview.png")

    env = os.environ.copy()
    env["DETECTED_COUNTS"] = ",".join(str(c) for c in counts)
    env["SNAPSHOT_PATH"] = out_path
    env["SNAPSHOT_SECONDS"] = "180"
    env["SDL_VIDEODRIVER"] = "dummy"      # never opens a window

    try:
        done = subprocess.run([sys.executable, "main.py"], cwd=sim_dir, env=env,
                              capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        status.config(text="Simulation render timed out.", fg=RED)
        return

    if not os.path.exists(out_path):
        detail = (done.stderr or done.stdout or "no output").strip().splitlines()
        status.config(text=f"Render failed: {detail[-1] if detail else '?'}", fg=RED)
        return

    show_simulation_image(out_path, counts)
    status.config(
        text=f"Model 2 seeded from detection  ·  W {counts[0]}  N {counts[1]}  "
             f"E {counts[2]}  S {counts[3]}", fg=GREEN)


def show_simulation_image(path, counts):
    """Displays the rendered frame in a resizable viewer window."""
    global _sim_window
    win = globals().get("_sim_window")
    if win is not None and win.winfo_exists():
        win.destroy()

    win = tk.Toplevel(root)
    _sim_window = win
    win.title("Model 2 — intersection seeded from detected demand")
    win.configure(bg=BG)

    tk.Label(win, text="Detected demand applied to the simulation",
             bg=BG, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(
                 anchor="w", padx=16, pady=(12, 0))
    tk.Label(win,
             text=f"Approach weights from YOLOv5 counts  ·  "
                  f"West {counts[0]}   North {counts[1]}   "
                  f"East {counts[2]}   South {counts[3]}",
             bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(
                 anchor="w", padx=16, pady=(0, 8))

    img = Image.open(path)
    # Fit the frame to the screen without distorting it
    max_w = min(int(win.winfo_screenwidth() * 0.85), img.width)
    scale = max_w / img.width
    img = img.resize((int(img.width * scale), int(img.height * scale)),
                     Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(win, image=photo, bg=BG)
    label.image = photo               # keep a reference
    label.pack(padx=16, pady=(0, 16))

    tk.Label(win, text=f"saved to {path}", bg=BG, fg=MUTED,
             font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 10))


# -- Header (Fixed top)
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=24, pady=(12, 4))
tk.Label(header, text="Vehicle Counter & Simulation Bridge", bg=BG, fg=TEXT,
         font=("Segoe UI", 18, "bold")).pack(anchor="w")
tk.Label(header, text="YOLOv5 perception pipeline ➔ Model 2 Adaptive Signal Controller",
         bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w")

# -- Footer (Fixed bottom)
footer = tk.Frame(root, bg=BG)
footer.pack(side="bottom", fill="x", padx=24, pady=(6, 12))

tk.Button(footer, text="1. COUNT VEHICLES", command=count_vehicles,
          bg=BORDER, fg=TEXT, activebackground=ACCENT, activeforeground=BG,
          relief="flat", padx=18, pady=8, cursor="hand2",
          font=("Segoe UI", 10, "bold")).pack(side="left")

tk.Button(footer, text="2. BUILD SIMULATION FROM DETECTION", command=build_simulation_view,
          bg=ACCENT, fg=BG, activebackground=GREEN, activeforeground=BG,
          relief="flat", padx=20, pady=8, cursor="hand2",
          font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)

status = tk.Label(footer, text="Upload approach images, count vehicles, then build the simulation view.",
                  bg=BG, fg=MUTED, font=("Segoe UI", 9))
status.pack(side="left", padx=10)

# -- Scrollable Body Container (Guarantees no cutoff on small screens)
body_frame = tk.Frame(root, bg=BG)
body_frame.pack(fill="both", expand=True, padx=24, pady=4)

canvas = tk.Canvas(body_frame, bg=BG, highlightthickness=0)
scrollbar = tk.Scrollbar(body_frame, orient="vertical", command=canvas.yview)
scroll_content = tk.Frame(canvas, bg=BG)

scroll_content.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# -- Compass Layout: North top, West/East flanking Center, South bottom
grid = tk.Frame(scroll_content, bg=BG)
grid.pack(expand=True, padx=4, pady=4)

cards = {}
cards["North"] = card(grid, "North")
cards["North"].grid(row=0, column=1, padx=8, pady=6, sticky="n")

cards["West"] = card(grid, "West")
cards["West"].grid(row=1, column=0, padx=8, pady=6, sticky="n")

# Center Intersection Graphic + Simulation Bridge Info
centre = tk.Frame(grid, bg=CARD, highlightbackground=BORDER, highlightthickness=1, padx=14, pady=12)
centre.grid(row=1, column=1, padx=8, pady=6, sticky="nsew")

try:
    inter = Image.open(f"{IMAGE_FOLDER_PATH}/intersection.png").resize(
        (110, 110), Image.Resampling.LANCZOS)
    inter_img = ImageTk.PhotoImage(inter)
    lbl = tk.Label(centre, image=inter_img, bg=CARD)
    lbl.image = inter_img
    lbl.pack(pady=(0, 4))
except Exception:
    tk.Label(centre, text="✛", bg=CARD, fg=BORDER,
             font=("Segoe UI", 36)).pack()

tk.Label(centre, text="INTERSECTION", bg=CARD, fg=TEXT,
         font=("Segoe UI", 10, "bold")).pack()
tk.Label(centre, text="Model 1 Detection\n↓\nModel 2 Controller", bg=CARD, fg=MUTED,
         font=("Segoe UI", 8), justify="center").pack(pady=4)

tk.Button(centre, text="Build Sim View", command=build_simulation_view,
          bg=GREEN, fg=BG, activebackground=ACCENT, activeforeground=BG,
          relief="flat", padx=12, pady=4, cursor="hand2",
          font=("Segoe UI", 9, "bold")).pack(pady=(4, 0))

cards["East"] = card(grid, "East")
cards["East"].grid(row=1, column=2, padx=8, pady=6, sticky="n")

cards["South"] = card(grid, "South")
cards["South"].grid(row=2, column=1, padx=8, pady=6, sticky="n")

root.mainloop()


