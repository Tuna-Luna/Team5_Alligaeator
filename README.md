# Alligaeator
## Capstone Design Project Team 5

## Overview
Alligaeator is an AI-powered nutrition assistant that combines a YOLOv5 food detector, an Arduino-driven load-cell scale, and an Android companion app. The system identifies a dish from a live webcam feed, measures its weight automatically, and reports calorie and macronutrient estimates through a mobile UI.

![Design Overview](./assets/design_overview.gif)

## Key Features
- Real-time food recognition powered by a custom-trained YOLOv5 model (`src/project/best2.pt`).
- Automated weight capture through an MG995 servo, HX711 load sensor, and Arduino firmware (`src/arduino/arduino.ino`).
- Nutrition lookup using per-gram macro data stored in `src/project/foods.json`, enabling instant calorie, carb, protein, and fat estimates.
- REST API built with FastAPI so the Android client (`src/application/MyApplication3.zip`) can request detections and control the hardware.
- Mechanical components and assembly-ready G-code/STL files (`3D/`) for the smart plate enclosure.

## Repository Tour
- `src/project/` – YOLOv5 inference utilities (`detect_api_final.py`), the FastAPI service (`android_respond_test.py`), dataset configs (`data.yaml`, `data2.yaml`), nutrition tables, and sample images (`food/`).
- `src/arduino/` – Arduino sketch that drives the MG995 servo, HX711 load cell, and optional I2C LCD for real-time weight display.
- `src/application/MyApplication3.zip` – Android Studio project that consumes the HTTP API and displays the nutrition report.
- `3D/` – Printable hinge, upper/lower plate, and enclosure parts in `.gcode`, `.3mf`, and `.stl` formats.
- `dataset.tar.gz` – Packaged training dataset used for YOLOv5 fine-tuning.
- `assets/` – Images and GIFs referenced in this README.

## System Architecture
The workflow starts with a webcam feed piped to a YOLOv5 model running on a Raspberry Pi or PC. Detected food classes are combined with real-time weight readings from the Arduino, and the FastAPI service exposes the combined nutrition information for the Android app.

![Implementation Overview](./assets/implementation.png)

## Hardware System
The hardware layer mounts a plate on a load cell amplified by an HX711 module while an MG995 servo clears or rotates the plate between servings (`src/arduino/arduino.ino`). The Arduino publishes weight readings over serial (9600 baud) and accepts simple text commands (`LEFT`, `RIGHT`, `STOP`), which the FastAPI server issues when the Android app triggers plate rotation or resets the tare.

## Software Pipeline
### YOLOv5 Detector
`detect_api_final.py` wraps YOLOv5’s `DetectMultiBackend`, handles webcam capture, writes snapshots to `./captures/`, and returns the top detection (default `max_det=1`). Sample stills for offline testing live under `src/project/food/`.

### Nutrition + API Layer
`android_respond_test.py` hosts a FastAPI service that:
- calls the detector with `best2.pt` to classify food from either `source=0` (webcam) or the static `food/` images,
- reads the current weight from the Arduino over `/dev/ttyACM0`,
- multiplies the weight by per-gram values stored in `foods.json`, and
- returns the totals to the Android app. The same service exposes `/rotate`, `/finish`, and `/init` endpoints for servo control.

### Android Client
The Android Studio project (`MyApplication3.zip`) hooks into the FastAPI endpoints, displays detection results, and records the calorie log directly on the phone.

### 3D Printable Enclosure
All mechanical components needed for the smart plate—upper/lower shell, hinge variants, and mounting plates—are available in the `3D/` folder as ready-to-print `.gcode` or editable `.3mf`/`.stl` files to reproduce the physical housing.

## Dataset & Training Notes
`data2.yaml` defines 15 labeled food categories (`bean sprouts`, `beef`, `chicken`, `egg`, `pork`, `garlic`, `green onion`, `kimchi`, `onion`, `potato`, `spam`, `banana`, `sweet potato`, `cherry tomato`, `chicken breast`). Training/validation images are expected in `../train/images` and `../valid/images`, respectively, and the archived dataset (`dataset.tar.gz`) mirrors those splits. Model fine-tuning follows the standard YOLOv5 workflow

## Demo
Watch the final demo to see the full workflow in action.

![Final Demo](./assets/demo_final.gif)
