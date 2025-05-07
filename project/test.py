# import cv2

# cap = cv2.VideoCapture(0)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# while True:
#     ret, frame = cap.read()
#     cv2.imshow('Display', frame)

#     if cv2.waitKey(1) == 27:
#         break
import serial
import time

serial_port = '/dev/ttyACM0'  # 실제 포트로 확인 후 변경
baudrate = 9600
serial_timeout = 0.1

# 시리얼 포트 열기
ser = serial.Serial(serial_port, baudrate, timeout=serial_timeout)

try:
    while True:
        # 버퍼에 데이터가 있으면 읽기
        if ser.in_waiting > 0:
            try:
                raw = ser.readline()
                line = raw.decode('utf-8', errors='ignore').strip()
                if line:
                    # 정수라면 int(), 소수점 가능하면 float()
                    serial_data = float(line)
                    print(serial_data)
            except ValueError:
                # 숫자 변환 실패 시 무시
                pass
        # 너무 빠르게 도는 것을 막기 위해 살짝 대기
        time.sleep(0.05)

except KeyboardInterrupt:
    print("종료합니다.")

finally:
    ser.close()
