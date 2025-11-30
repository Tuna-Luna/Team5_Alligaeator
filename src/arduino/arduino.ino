#include <Servo.h>
#include "HX711.h"
#include "LiquidCrystal_PCF8574.h"

// 서보모터 설정
Servo mg995;
const int servoPin = 10;
int currentAngle = 90;  // 현재 각도

// 로드셀 설정
const int DT_PIN = 6;
const int SCK_PIN = 5;
const float scale_factor = 434.16;
HX711 scale;

// LCD 설정 (원하면 사용 가능)
LiquidCrystal_PCF8574 lcd(0x27);  // 일반 주소 0x27 또는 0x3F

// 시리얼 명령 수신 버퍼
String command = "";

void setup() {
  Serial.begin(9600);
  Serial.println("Initializing the scale");

  // 서보 초기화
  mg995.attach(servoPin);
  mg995.write(currentAngle);

  // 로드셀 초기화
  scale.begin(DT_PIN, SCK_PIN);

  // LCD 초기화 (필요 시 주석 해제)
  lcd.begin(16, 2);
  lcd.setBacklight(255);
  lcd.clear();

  Serial.println("Before setting up the scale:");
  Serial.println(scale.get_units(5), 0);  // 설정 전 값 출력

  scale.set_scale(scale_factor);         // 스케일 설정
  scale.tare();                          // 영점 보정

  Serial.println("After setting up the scale:");
  Serial.println(scale.get_units(5), 0);  // 설정 후 값 출력

  Serial.println("System Ready. Type LEFT / RIGHT / STOP.");
}

void loop() {
  // -----------------------------
  // 1. 무게 측정 및 출력
  // -----------------------------
  float weight = scale.get_units(10);
  if (weight <= 0) weight = 0;

  // 정수만 출력
  Serial.println(round(weight));

  // LCD 출력 (원하면 사용 가능)
  // lcd.clear();
  // lcd.setCursor(0, 0);
  // lcd.print("Weight:");
  // lcd.setCursor(0, 1);
  // lcd.print(round(weight));
  // lcd.print(" g");

  scale.power_down();
  delay(500);
  scale.power_up();

  // -----------------------------
  // 2. 시리얼 명령 처리
  // -----------------------------
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (command.length() > 0) {
        handleCommand(command);
        command = "";
      }
    } else {
      command += c;
    }
  }
}

// -----------------------------
// 명령 처리 함수
// -----------------------------
void handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "LEFT") {
    //currentAngle = constrain(currentAngle - 45, 0, 180);
    mg995.write(50);
    delay(600);  //각도를 시간으로 조절
    mg995.write(70);
    delay(500);
    mg995.write(90);
    currentAngle = 90;
  }
  else if (cmd == "RIGHT") {
    //currentAngle = constrain(currentAngle + 45, 0, 180);
    mg995.write(150);
    delay(1390);  //각도를 시간으로 조절
    mg995.write(100);
    delay(1300);
    mg995.write(90);
    //scale.tare();
    //currentAngle = 90;
  }
  else if (cmd == "STOP") {
    mg995.write(90);
    currentAngle = 90;
    scale.tare();
  }

  // Serial.print("ACK: ");
  // Serial.println(cmd);
}
