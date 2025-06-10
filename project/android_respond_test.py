# sudo ufw allow 8000
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI
from fastapi.responses import JSONResponse
# from detect_api import detect_objects  # 앞서 설명한 함수
from detect_api_final import detect_objects

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


ser = serial.Serial(serial_port, baudrate, timeout=serial_timeout)
def detect_weights():
    #ser = serial.Serial(serial_port, baudrate, timeout=serial_timeout)
    serial_data = 0
    count = 0
    ser.reset_input_buffer()
    time.sleep(0.05)
    while not serial_data:
    #while True:
   # while count < 3:
        if ser.in_waiting>0:
            try:
                count += 1
                raw = ser.readline()
                line = raw.decode('utf-8', errors='ignore').strip()
                if line:
                    serial_data = float(line)
                    print(serial_data)
            except ValueError:
                pass
    time.sleep(0.1)

#    finally:
#        ser.close()
    return serial_data
    

app = FastAPI()

# @app.post("/detect")
@app.api_route("/detect", methods=["GET", "POST"])
def detect():
    try:
        food_item = detect_objects(
            weights='best2.pt',
            #source=f'./kimchi.jpg',
            #source = 0,
            device='cpu',
            temp_img_save_path='./captures/captured.jpg'
        )
        
        weights = detect_weights()
        food_db = FOOD_DB.get(food_item[0][0]['name'], None)
        print(weights)
        #weights = 100
        return JSONResponse(content={
            "name": food_item[0][0]['name'],
            "weights": weights,
            "cal": round(food_db['cal'] * weights, 2),
            "carbs": round(food_db['carbs'] * weights, 2),
            "protein": round(food_db['protein'] * weights, 2),
            "fat": round(food_db['fat'] * weights, 2)
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.api_route("/rotate", methods=["GET"])
def rotate_motor():
    print("rotate start")
    #ser = serial.Serial(serial_port, baudrate, timeout=serial_timeout)
    time.sleep(0.05)

    try:
        ser.write(b'RIGHT\n')
        print("Success!")
    finally:
        print("no")
       # ser.close()

@app.api_route("/finish", methods=["GET"])
def exit():
    print("finished")
    #ser = serial.Serial(serial_port, baudrate, timeout=serial_timeout)
    time.sleep(0.05)

    try:
        ser.write(b'LEFT\n')
        print("Success!")
    finally:
        ser.close()
# @app.get("/detect")
# def detect_get():
#     return {"name": "kimchi", "weights": 100, "cal": 21.0, "carbs": 4.07, "protein": 1.65, "fat": 0.22}

@app.api_route("/init", methods=["GET"])
def init():
    print("init")
    time.sleep(0.05)

    try:
        ser.write(b'STOP\n')
        print("Success!")
    finally:
        print("end")
