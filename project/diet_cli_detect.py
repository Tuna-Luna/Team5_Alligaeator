#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List

from nutrition_db import FOOD_DB
# from detect_helper import run_detection
from detect_api import detect_objects
# from detect_api_weights import detect_objects

@dataclass
class BodyStats:
    gender: str 
    age : int 
    weight : float 
    height : float

@dataclass
class MacroOut:
    cal: float
    carbs: float   # g
    protein: float # g
    fat: float     # g

@dataclass
class FoodLogItem:
    food: str
    weight: float  # g
    kcal: float
    protein: float
    carbs: float
    fat: float

@dataclass 
class TotalOut:
    kcal : float
    carbs : float 
    protein : float 
    fat : float 

def calculate_macros(bs : BodyStats) -> dict:
    # 대충한거
    if bs.gender == 'female':
        cal = bs.weight * bs.age * bs.height
        carbs   = 0.50 * cal / 4      # g
        protein = 0.30 * cal / 4
        fat     = 0.20 * cal / 9
    else:
        cal = bs.weight * bs.age * bs.height + 1000
        carbs   = 0.50 * cal / 4      # g
        protein = 0.30 * cal / 4
        fat     = 0.20 * cal / 9   
    body_info = MacroOut(
        cal = cal,
        carbs = carbs,
        protein = protein,
        fat = fat 
    )

    return body_info   

class DietManager:
    def __init__(self):
        self.log: List[FoodLogItem] = []

    def add_detected_food(self, weight: float, img_name: str) -> FoodLogItem:
        # 1) YOLOv5 실행 → 전체 결과 리스트 반환
        all_dets = detect_objects(
            weights='best.pt',
            # source=f'./{img_name}.jpg',
            source = '0',
            device='cpu'
        )
        # all_dets = detect_objects(
        #     weights='best.pt',
        #     # source=f'./{img_name}.jpg',
        #     source = '0',
        #     device='cpu',
        #     serial_port : str = '/dev/ttyUSBo'
        # )

        # 2) 빈 결과 처리
        if not all_dets or not all_dets[0]:
            raise ValueError("No object detected")

        # 3) 첫 번째 detection의 class_id 추출
        first_det = all_dets[0][0]
        cls_id = first_det['class_id']   # 이건 이제 int 타입!

        # 4) FOOD_DB 조회
        if cls_id not in FOOD_DB:
            raise ValueError(f"class {cls_id} not in FOOD_DB")
        base = FOOD_DB[cls_id]           # OK!

        # 5) 영양 계산
        ratio = weight / 100.0
        item = FoodLogItem(
            food    = base["food"],
            weight  = weight,
            kcal    = round(base["kcal"]    * ratio, 2),
            protein = round(base["protein"] * ratio, 2),
            carbs   = round(base["carbs"]   * ratio, 2),
            fat     = round(base["fat"]     * ratio, 2),
        )
        self.log.append(item)
        return item

    def total(self):
        total_result = TotalOut(
            kcal = sum(i.kcal    for i in self.log),
            protein = sum(i.protein for i in self.log),
            carbs = sum(i.carbs   for i in self.log),
            fat = sum(i.fat     for i in self.log)
        )

        return total_result

def main():
    dm = DietManager()
    print("scan <weight_g>  → 웹캠 감지 후 해당 무게 적용")
    print("total            → 누적 영양소")
    print("exit             → 종료\n")

    while True:
        try:
            cmd, *args = input("> ").split()
        except ValueError:
            continue
        except (EOFError, KeyboardInterrupt):
            break

        if cmd == "calc":
            if len(args) != 4:
                print("Usage: calc <gender> <age> <weight_kg> <height_cm>")
                continue
            gender, age, weight, height = args
            bs = BodyStats(gender, int(age), float(weight), float(height))
            res = calculate_macros(bs)
            print(res)
            print(f"Result → kcal:{res.cal} | carbs:{res.carbs}g "
                  f"| protein:{res.protein}g | fat:{res.fat}g")

        elif cmd == "scan":
            if not args:
                print("Usage: scan <weight_g>")
                continue
            w = float(args[0])
            img_name = args[1]
            try:
                item = dm.add_detected_food(w, img_name)
                print(f"Added {item.food} ({item.weight}g) → "
                      f"{item.kcal} kcal Protein : {item.protein} Carbs : {item.carbs} Fat : {item.fat}")
            except Exception as e:
                print("Error:", e)

        elif cmd == "total":
            t = dm.total()
            if t:
                print(f"Total → {t.kcal} kcal "
                      f"Protein : {t.protein} Carbs : {t.carbs} Fats : {t.fat}")
            else:
                print("No items yet.")

        elif cmd in {"exit", "quit"}:
            break

if __name__ == "__main__":
    main()
