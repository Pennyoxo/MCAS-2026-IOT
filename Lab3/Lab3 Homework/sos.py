import RPi.GPIO as GPIO
import time

LED_PIN = 11       # LED：實體腳位 11 (BCM GPIO17)
BUZZER_PIN = 13    # 蜂鳴器：實體腳位 13 (BCM GPIO27)
FREQ = 523         # 蜂鳴器頻率 (523Hz，大約是 C5)
UNIT = 0.2         # 摩斯密碼的 1 個單位時間 (秒)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer = GPIO.PWM(BUZZER_PIN, FREQ)


def signal(units):
    """LED 亮 + 蜂鳴器響 units 個單位，然後一起停 1 個單位"""
    GPIO.output(LED_PIN, GPIO.HIGH)
    buzzer.start(50)
    time.sleep(units * UNIT)
    GPIO.output(LED_PIN, GPIO.LOW)
    buzzer.stop()
    time.sleep(UNIT)            # 同一字母內，音與音之間停 1 單位


def dot():                      # 短音 ·
    signal(1)


def dash():                     # 長音 —
    signal(3)


def letter_s():                 # S = · · ·
    for _ in range(3):
        dot()


def letter_o():                 # O = — — —
    for _ in range(3):
        dash()


try:
    while True:
        print("S")
        letter_s()
        time.sleep(2 * UNIT)    # 字母之間停 3 單位 (signal 已經停過 1 單位，再補 2)
        print("O")
        letter_o()
        time.sleep(2 * UNIT)
        print("S")
        letter_s()
        print("--- SOS ---")
        time.sleep(6 * UNIT)    # 每次 SOS 之間停 7 單位 (已停 1，再補 6)

except KeyboardInterrupt:
    pass
finally:
    buzzer.stop()
    GPIO.cleanup()
