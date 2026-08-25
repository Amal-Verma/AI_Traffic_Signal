# Demo asset provenance

## india_crossroads.mp4 (`assets/examples/videos/`)

Source: Pixabay — "India, Crossroads, Traffic"
https://pixabay.com/videos/india-crossroads-traffic-busy-road-8698/

Licence: Pixabay Content License — free for commercial use, no attribution
required. Attribution recorded here anyway for traceability.

Processing: first 15 seconds, scaled 1920x1080 -> 960x540, audio removed.

## tracking_demo.mp4

`model1/VehicleTracker.py` (YOLOv8s + ByteTrack + supervision LineZone) run
over the clip above with a vertical counting line at x=470.

Result: 17 in / 31 out over 450 frames, 97s of CPU time (~4.6 fps).

Known limitation visible in the footage: auto-rickshaws are not boxed. COCO
has no auto-rickshaw class, so they are either missed or absorbed into "car".
Addressing this needs fine-tuning on an Indian dataset such as IDD-Detection
or DriveIndia.

## before_after.png, before_fixed.png, after_adaptive.png, demo.mp4

Rendered from this repository's own simulation. Identical demand (YOLOv5
counts of the four sample approach images: W 75, N 84, E 13, S 51), identical
random seed, 600 simulated seconds measured. Only the controller differs.

## detections/

YOLOv5s detections on `assets/examples/images`, confidence 0.15.
