# Demo run sheet — 11 minutes

## Before you start

Two terminals, both already in place:

```fish
# Terminal A — detection
cd ~/Github/AI_Traffic_Signal/model1
../.venv/bin/python model1_gui.py

# Terminal B — simulation (don't launch yet)
cd ~/Github/AI_Traffic_Signal/model2/Simulation/Traffic-Simulation
../../../.venv/bin/python main.py
```

Checklist: laptop on mains, notifications off, terminal font large, browser closed.
Have `assets/examples/images/` open in the file dialog's default location.

**Read the numbers off the screen. Do not quote memorised figures** — the live
HUD is computed in front of the audience and is always right.

---

## 1 · The problem (1 min, no software)

Fixed-timer signals can't respond to demand. Say the three costs the problem
statement names: **waiting time, fuel, emissions**. Say what you built: a
camera-fed controller that reallocates green time every cycle.

Don't open anything yet. Let them hold the problem for a moment.

---

## 2 · Perception (2 min) — Terminal A

The GUI is already open. Upload the four approach images:
`north.jpg`, `south.jpg`, `east.png`, `west.jpg`.

Press **1. COUNT VEHICLES**. Under a second for all four.

Point at the per-approach weighted demand: **W 75 · N 84 · E 13 · S 51**.
That asymmetry is the whole point — a fixed timer gives East the same green as
North despite six times less traffic.

**Name the limitation here, before anyone asks.** COCO-pretrained YOLO has no
autorickshaw class and undercounts two-wheelers in dense Indian traffic. Say
the fix out loud: fine-tune on IDD-Detection / DriveIndia. Naming it yourself
is strength; being caught by it is not.

---

## 3 · The bridge (1 min) — the money shot

Press **2. BUILD SIMULATION FROM DETECTION**.

An image of the simulation appears, seeded with those exact counts. Header
reads **DETECTED FROM CAMERA · YOLOv5 — W 75 N 84 E 13 S 51**.

Point at *Queue by approach*: North longest, East shortest — the queues track
the detection. This is perception driving control, in one picture.

---

## 4 · Live control (3 min) — Terminal B

Launch the simulation. Press **`H`** immediately to hide the controls panel.

Orient them: four approaches, three lanes each, twelve signal groups, each
vehicle following an Intelligent Driver Model. Green and red heads at the
stop lines.

Point at **Phase** and **Green remaining** counting down — that is the
controller thinking. Watch a phase change and the queue bars reorder.

Press **`5`** for real measured demand: NYC DOT counts for Junction Blvd ×
Northern Blvd, Queens. Both the approach mix and the spawn rate come from the
data. Press **`.`** a couple of times to walk through the day and show demand
rising into the evening peak.

---

## 5 · The A/B (3 min) — the argument

Press **`T`**. The badge flips green → amber, **ADAPTIVE** → **FIXED-TIME**,
and the phase count drops from 8 to 6.

**Let it run a full minute.** The cycle is 100 simulated seconds; at 10x that
is ten seconds per cycle, and you need several cycles before the numbers settle.
Talk over it — this is when you explain how green time is allocated.

Then read off the screen, in this order:

1. **Avg delay/vehicle** — the metric the problem statement names first
2. **Avg stopped/vehicle** and **Stop events**
3. **Fuel per vehicle**
4. **Total delay** — if it climbs while the average holds, the intersection is
   falling behind

Press **`T`** back to adaptive and let it settle again for the comparison.

**Do not say throughput improves.** At real demand the intersection is not
saturated, so both controllers clear nearly everything that arrives and
throughput is capped by arrivals, not by signal quality. The honest claim is
lower delay, fewer stops, less fuel *at the same throughput* — which is a
stronger claim anyway.

---

## 6 · Limits and next steps (1-2 min)

Close on what you know is not yet solved. This is the most credible part.

- **Saturation.** Above roughly 100 vehicles/min the current allocation stops
  beating a fixed plan. Diagnosed: it allocates from peak queue occupancy, and
  once every approach saturates those counts stop discriminating. Fix is to
  allocate on arrival rate or discharge rate instead.
- **Perception.** No autorickshaw class; two-wheelers undercounted.
  Fine-tune on IDD-Detection / DriveIndia.
- **Mixed traffic.** Lane-based car-following does not model filtering, which
  is a large part of real Indian junction capacity.
- **Real baseline.** Bengaluru Traffic Police publish deployed signal timings
  (146-190s cycles, time-of-day plans). Beating a real deployed plan is the
  next validation, and a stronger claim than beating an even split.

---

## If something goes wrong

| symptom | fix |
|---|---|
| numbers look wrong right after `T` | that's the transient — wait, or press `R` |
| simulation stutters | press `-` to lower sim speed |
| want a clean restart | press `C` |
| detection GUI won't start | needs `~/.cache/torch/hub`; do not clear it |

**Don't press `]` to raise traffic on stage.** Above ~100 veh/min the adaptive
controller currently loses, and that is visible on screen.

---

## Key reference

| key | action |
|-----|--------|
| `SPACE` | pause / resume |
| `T` | adaptive ↔ fixed-time (resets measurement window) |
| `5` | real measured NYC demand |
| `,` `.` | hour of day (real data only) |
| `1`–`4` | synthetic scenarios |
| `R` | reset measurement window |
| `C` | clear traffic and restart |
| `-` `=` | sim speed down / up |
| `H` | hide/show controls panel |
| `Q` / `ESC` | quit |
