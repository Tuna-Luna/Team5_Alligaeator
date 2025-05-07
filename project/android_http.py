# sudo ufw allow 8000
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from detect_api import detect_objects  # 앞서 설명한 함수

import json
# https://www.fatsecret.co.uk/calories-nutrition/generic/bean-sprouts?portionamount=100.000&portionid=4617891
with open('foods.json', 'r', encoding='utf-8') as f:
    FOOD_DB = json.load(f)

def get_food_info(name: str):
    return FOOD_DB.get(name, None)

# arduino
import serial
import time

serial_port = '/dev/ttyACM0'  # 실제 포트로 확인 후 변경
baudrate = 9600
serial_timeout = 0.1


def detect_weights():
    ser = serial.Serial(serial_port, baudrate, timeout=serial_timeout)
    serial_data = 0
    try:
        while not serial_data:
            if ser.in_waiting >0:
                try:
                    raw = ser.readline()
                    line = raw.decode('utf-8', errors='ignore').strip()
                    if line:
                        serial_data = float(line)
                except ValueError:
                    pass
            
            time.sleep(0.05)
    finally:
        ser.close()
    return serial_data
    

import traceback
app = FastAPI()
toggle_state = {"use_kimchi": False}

# @app.post("/detect")
@app.api_route("/detect", methods=["GET", "POST"])
def detect():
    try:
        toggle_state["use_kimchi"] = not toggle_state["use_kimchi"]
        img_file = 'kimchi.jpg' if toggle_state["use_kimchi"] else 'spam.jpg'
        print(f"Serving image: {img_file}")
        food_item = detect_objects(
            weights='best.pt',
            # source=f'./{img_file}',
            source=0,
            device='cpu'
        )

        weights = detect_weights()
        print(weights)
        ###########################3
        if food_item[0][0]['name'] == 'photato':
            food_item[0][0]['name'] = 'potato'
        elif food_item[0][0]['name'] == 'fork':
            food_item[0][0]['name'] = 'pork'
        #####################
        food_db = FOOD_DB.get(food_item[0][0]['name'], None)
        # weights = 100
        # img = 'spam'
        return JSONResponse(content={
            "name": food_item[0][0]['name'],
            "weights": weights,
            "cal": round(food_db['cal'] * weights, 2),
            "carbs": round(food_db['carbs'] * weights, 2),
            "protein": round(food_db['protein'] * weights, 2),
            "fat": round(food_db['fat'] * weights, 2)
        })
    except Exception as e:
        print("🔥 ERROR:", e)
        traceback.print_exc()
        return JSONResponse(status_code=400, content={"error": str(e)})
