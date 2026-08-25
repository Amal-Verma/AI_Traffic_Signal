# AI Traffic Signal

An adaptive traffic-signal controller for a four-way intersection, plus the
simulation used to evaluate it.

Two halves:

| | what it does |
|---|---|
| **model1** | Counts vehicles per approach from images/video with YOLO |
| **model2** | Allocates green time from those counts, and simulates the result |

The controller reads a per-approach, per-lane vehicle count and decides both
the **phase order** and the **green duration** for each phase of a 100-second
cycle. The simulation is a microscopic Intelligent Driver Model built on pygame.

---

## Setup

Requires **Python 3.11**. The pinned dependencies have no wheels for 3.12+,
and `torch 2.3.1` ships none above cp312.

```bash
git clone <your-repo-url>
cd AI_Traffic_Signal

python3.11 -m venv .venv
source .venv/bin/activate           # fish: source .venv/bin/activate.fish
```

Install torch first, from the CPU index:

```bash
pip install torch==2.3.1 torchvision==0.18.1 \
    --index-url https://download.pytorch.org/whl/cpu
```

Then the rest:

```bash
grep -v '^torch' requirements.txt > /tmp/req.txt
pip install -r /tmp/req.txt "supervision==0.22.0" "opencv-python==4.11.0.86"
```

Two pins matter and are not in `requirements.txt`:

- **`supervision==0.22.0`** — 0.30 removed `sv.BoundingBoxAnnotator`, which
  `model1/VehicleTracker.py` uses.
- **`opencv-python==4.11.0.86`** — 5.x pulls numpy 2.x and breaks the
  `scipy==1.11.4` pin.

`torch`'s own `--index-url` line inside `requirements.txt` is rejected by
`uv pip`, which is why it is installed separately above.

### Cache the model weights

Both detectors download weights on first use. Do this once while you have a
network, or the first run offline will fail:

```bash
cd model1
python -c "import torch; torch.hub.load('ultralytics/yolov5','yolov5s')"
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
```

---

## Running the simulation

```bash
cd model2/Simulation/Traffic-Simulation
python main.py
```

A window opens showing the intersection, a live metrics panel, and the current
signal phase.

### Controls

| key | action |
|-----|--------|
| `SPACE` | pause / resume |
| `T` | toggle adaptive vs fixed-time control |
| `R` | reset the measurement window |
| `C` | clear all traffic and restart |
| `[` `]` | spawn rate down / up |
| `1`–`4` | synthetic traffic scenario: Balanced, Morning peak, Evening peak, North corridor |
| `5` | real measured demand from NYC DOT counts |
| `,` `.` | step the hour of day, real data only |
| `-` `=` | simulation speed down / up |
| `H` | show/hide the controls panel |
| `Q` / `ESC` | quit |

Mouse wheel zooms; drag pans.

### Comparing the two controllers

`T` switches between:

- **Adaptive** — `CycleCalc2` picks phase order and green split from measured
  per-lane demand each cycle.
- **Fixed-time** — the same phases with green split evenly, ignoring demand.
  It pays the same all-red clearance the adaptive cycle does, so the two differ
  only in *allocation*.

Switching resets the measurement window so the numbers on screen always
describe the controller currently running.

**Let it run.** The cycle is 100 simulated seconds; over anything shorter than
about four cycles the metrics are transient and can point the wrong way.

**Read the right metric.** At the default 75 vehicles/min the intersection is
not saturated, so both controllers clear nearly everything that arrives and
throughput is capped by the spawn rate rather than by signal quality. The
meaningful differences are in **fuel per vehicle**, **stop events**, and
**queue length**.

### Real measured demand

Key `5` drives the simulation from **NYC DOT Automated Traffic Volume Counts**
(dataset `7ym2-wayt`) for Junction Boulevard × Northern Boulevard in Queens,
an intersection where all four approaches were actually counted. Both the
approach mix and the spawn rate come from the measurements; `,` and `.` step
through the 24-hour curve.

The bundled profile lives in
`model2/Simulation/Traffic-Simulation/data/nyc_junction_northern.json`, with
its provenance and caveats recorded alongside the numbers. `trafficSim/real_traffic.py`
loads it. If the file is missing the simulation falls back to the synthetic
scenarios rather than failing.

Northern Boulevard (East/West approaches) carries roughly three times the daily
volume of Junction Boulevard (North/South) — a real arterial asymmetry, and the
case adaptive allocation is meant to exploit.

Note the counted days differ per approach: the East approach rests on a single
counted day and is correspondingly noisier.

The scenarios on `1`–`4` are synthetic illustrative shapes, not measurements.

### Tuning

`model2/Simulation/Traffic-Simulation/configCustom.py`:

| field | meaning |
|---|---|
| `pRoad` | approach mix, in order West, North, East, South |
| `pLane` | lane mix within an approach |
| `vehicles` | vehicle type mix: car, truck, bus, motorcycle |
| `vehicle_rate` | spawn rate per minute |

`main.py` holds the road geometry, the path set, and `STEPS_PER_UPDATE`
(simulated seconds per wall second).

### Debug output

Silent by default. For the per-cycle controller trace:

```bash
TRAFFICSIM_DEBUG=1 python main.py
```

---

## Running vehicle detection

### Per-approach counts from still images

```bash
cd model1
python model1_gui.py
```

Upload an image for each approach (samples in `assets/examples/images`), then
press **COUNT VEHICLES**. Each approach reports cars, bikes, buses and trucks
plus a weighted demand figure — the weighting is `cnt_ratio` in
`VehicleCounter`, defaulting to `[1,2,3]` for bike:car:truck.

Roughly 0.2s per image on CPU.

### Line-crossing counts from video

```bash
cd model1
python VehicleTracker.py
```

Opens a file picker, shows the first frame so you can draw a counting line,
then runs YOLOv8 + ByteTrack over the video and writes an annotated copy
alongside the source. Sample video in `assets/examples/videos`.

Counts every COCO vehicle class (car, motorcycle, bus, truck) — see
`VEHICLE_CLASSES` in `VehicleTracker.py`.

This runs at roughly **4.6 fps on CPU**, about 6x slower than realtime, so it
is not suitable for live demonstration. A pre-rendered output is kept at
`assets/demo/tracking_demo.mp4`.

Note the bundled sample clip is motorway footage, not Indian junction traffic;
the line-crossing counts it produces are not what the signal controller
consumes (that reads per-approach queue counts from stills).

### As a library

```python
from model1.VehicleCounter import VehicleCounter

vc = VehicleCounter()
total, (cars, bikes, buses, trucks) = vc.count('path/to/image.jpg')
left, middle, right = vc.count_lanewise('path/to/image.jpg')
```

`count_lanewise` prompts you to draw two lane-dividing lines on the image, and
returns the weighted count per lane — this is the shape the signal controller
consumes.

---

## Layout

```
model1/                     vehicle detection
  VehicleCounter.py           YOLOv5 still-image counts, whole-frame and per-lane
  VehicleTracker.py           YOLOv8 + ByteTrack line-crossing counts on video
  model1_gui.py               tkinter front-end for the four approaches
  my_utility.py               interactive line/point pickers

model2/
  Algorithm/CycleCalc2.py     phase ordering and green-time allocation
  Simulation/Traffic-Simulation/
    main.py                   geometry, paths, signal groups, entry point
    configCustom.py           traffic mix and spawn rate
    trafficSim/
      simulation.py             the update loop
      vehicle.py                Intelligent Driver Model
      road.py                   per-road car-following and signal response
      traffic_signal.py         controller, adaptive and fixed-time
      vehicle_generator.py      spawns vehicles by approach and lane
      window.py                 rendering, HUD and controls

assets/examples/            sample images and video
DEMO.md                     presentation run sheet
```

## Known limitations

- No conflict-point checking inside the intersection — vehicles on crossing
  turn paths can overlap.
- All drivers share identical IDM parameters, so traffic looks uniform.
- No lane changing.
- Vehicles enter the map already at their target speed.
- The adaptive controller's advantage narrows and can reverse once the
  intersection is saturated, where throughput becomes bound by total green
  time rather than by how it is allocated.

## Acknowledgements

- **YOLOv5 / YOLOv8** by [Ultralytics](https://github.com/ultralytics/yolov5).
- The simulation is built on a traffic-flow model
  [described here](https://muddy-vulture-d01.notion.site/The-Modelling-of-Simpang-Empat-Pingit-Crossroad-a7f1a8adf0d44317aebff998149494b9?pvs=25).
