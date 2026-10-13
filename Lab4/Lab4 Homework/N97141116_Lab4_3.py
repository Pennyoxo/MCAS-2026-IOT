import serial
import time
import RPi.GPIO as GPIO

# LED 設定（跟 Lab3 一樣，用實體腳位 11）
LED_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

# 設定 UART 連接埠與參數（p.30）
ser = serial.Serial(
    port='/dev/serial0',   # 對應 GPIO14 (TX) 和 GPIO15 (RX)
    baudrate=9600,         # 傳輸速率
    timeout=1              # 讀取逾時設定（秒）
)

# 傳送資料（p.31）
def send_data(data):
    if ser.is_open:
        ser.write(data.encode('utf-8'))
        print(f"已傳送：{data.strip()}")

# 接收資料（p.31）
def receive_data():
    if ser.is_open:
        incoming = ser.readline().decode('utf-8').strip()
        if incoming:
            print(f"收到資料：{incoming}")
        return incoming

# 讓 LED 閃 times 次
def blink(times):
    for _ in range(times):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.3)

# 主程式（p.32，改成送出 1~5 的數字）
try:
    count = 1
    while True:
        send_data(f"{count}\n")
        time.sleep(1)
        data = receive_data()

        if data.isdigit():
            print(f"LED 閃 {data} 下")
            blink(int(data))

        count = count % 5 + 1   # 1→2→3→4→5→1→...
        time.sleep(1)


except KeyboardInterrupt:
    print("程式中斷")

finally:
    if ser.is_open:
        ser.close()
        print("串列埠已關閉")
    GPIO.cleanup()
